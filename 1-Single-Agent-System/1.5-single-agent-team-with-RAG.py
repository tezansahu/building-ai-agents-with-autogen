import os
import sys
import requests
import json
from dotenv import load_dotenv
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.tools.langchain import LangChainToolAdapter
from autogen_agentchat.ui import Console
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools.retriever import create_retriever_tool


load_dotenv(os.path.join("..", ".env"))

##############################################################################

# Define the LangChain Tool for RAG using ChromaDB

async def get_rag_tool():
    # Populate the ChromaDB with initial content.
    print("Loading documents into the vector store...")

    files = os.listdir(os.path.join(os.path.dirname(__file__), "documents"))
    pages = []

    for file in files:
        if file.endswith(".pdf"):
            file_path = os.path.join(os.path.dirname(__file__), "documents", file)
            loader = PyPDFLoader(file_path)

            async for page in loader.alazy_load():
                pages.append(page)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )
    doc_splits = text_splitter.split_documents(pages)

    # Add to vectorDB
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),     # First run will download the model & may tak a while
    )

    print("Vector Store populated with contents from the PDF file.\n")

    retriever = vectorstore.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="retriever_tool",
        description="A tool to retrieve AI research papers and documents.",
    )

    return retriever_tool



##############################################################################



async def main() -> None:
    # Create the Client
    model_client = AzureAIChatCompletionClient(
        model="gpt-4o-mini",
        endpoint="https://models.inference.ai.azure.com",
        # To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings.
        credential=AzureKeyCredential(os.getenv("GITHUB_TOKEN")),
        model_info={
            "json_output": True,
            "function_calling": True,
            "vision": True,
            "family": "unknown",
        },
    )
    
    rag_tool = await get_rag_tool()

    # Define an AssistantAgent with the model, tools & system message
    # The system message instructs the agent via natural language.
    rag_agent = AssistantAgent(
        name="rag_agent",
        model_client=model_client,
        # Create the LangChain tool adapter for the RAG tool.
        tools=[LangChainToolAdapter(rag_tool)],
        system_message="You are a research assistant agent. You will be provided with a tool to retrieve documents from a vector database. Use this tool to answer th user's questions. If you cannot find the answer, please respond with 'I don't know'.",
    )

    # Termination condition that stops the task if the agent responds with a text message.
    termination_condition = TextMessageTermination("rag_agent")

    # Create a team with the RAG agent and the termination condition.
    team = RoundRobinGroupChat(
        [rag_agent],
        termination_condition=termination_condition,
    )

    task = input("Enter your task: ")  # Get the user input for the task.

    # # For single-turn conversation, you can use the following code:
    # await Console(team.run_stream(task=task))

    # For multi-turn conversation, you can use the following code:
    while True:
        stream = team.run_stream(task=task)
        await Console(stream)

        # Get the user response.
        task = input("\nContinue the conversation (type 'exit' to leave): ")
        if task.lower().strip() == "exit":
            break

    await model_client.close()


if __name__ == "__main__":
    # Solution for Windows users
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())

# ------------------------------------------------
# Example tasks to test the agent's response.
# ------------------------------------------------
# 1. What is the speciality of Gemma 3 model?
# 2. How does it compare to Phi-4?
# 3. Explain the RL techniques used in Search-R1 like I am a noob.