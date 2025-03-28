import os
import sys
import requests
import json
from dotenv import load_dotenv
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.memory import MemoryContent, MemoryMimeType
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
from autogen_agentchat.ui import Console
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential


load_dotenv(os.path.join("..", ".env"))

##############################################################################

# Define the tools for the agent

def serper_web_search(query: str) -> str:
    """
    Perform a web search using the Serper API and return the results.

    Args:
        query (str): The search query.

    Returns:
        str: The search results in JSON format.
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "gl": "in"
    })
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    return response.text
    

def write_report(content: str, filename: str) -> str:
    """
    Write contents to a file, in the form of a report.

    Args:
        content (str): The content to write to the file.
        filename (str): The name of the file.
    
    Returns:
        str: Status of the file writing operation.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        return f"Content written to: {filename}"
    except Exception as e:
        return f"Error: {str(e)}"

##############################################################################
##############################################################################

# Define the memory for the agent

async def populate_memory():
    print("Populating memory...")
    # Initialize ChromaDB memory with custom config
    # (First run may take som time to download the "all-MiniLM-L6-v2" ONNX Model used to vectorize the text)
    chroma_user_memory = ChromaDBVectorMemory(
        config=PersistentChromaDBVectorMemoryConfig(
            collection_name="preferences",
            persistence_path=os.path.join(".", ".chromadb_autogen"),
            k=2,  # Return top k results
            score_threshold=0.2,  # Minimum similarity score
        )
    )

    # memory = [
    #     "I have a strong background in machine learning and want to transition into product management.",
    #     "I prefer working in fast-paced startup environments.",
    #     "I value work-life balance and prefer remote work.",
    #     "I'm interested in leadership roles and cross-functional collaboration.",
    #     "I want to explore AI-related products and solutions."
    # ]

    memory = [
        "I have a background in machine learning and prefer working in large, established companies.",
        "I value job stability over rapid growth.",
        "I'm interested in working with large-scale data infrastructure.",
        "I prefer working on deep technical problems rather than people management.",
        "I want to focus on technical excellence instead of conventional leadership roles.",
    ]

    for m in memory:
        await chroma_user_memory.add(
            MemoryContent(
                content=m, 
                mime_type=MemoryMimeType.TEXT,
                metadata={"category": "preferences"}
            ),
        )
    
    return chroma_user_memory

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

    chroma_user_memory = await populate_memory()  # Populate the memory with initial content.

    # Define an AssistantAgent with the model, tools & system message
    # The system message instructs the agent via natural language.
    career_mentor_agent = AssistantAgent(
        name="career_mentor_agent",
        model_client=model_client,
        tools=[serper_web_search, write_report],
        # We remove the reflect_on_tool_use here because that generates a text message, which would be considered as a termination condition.
        system_message="You are a Career Mentor Agent with deep expertise in career development, professional growth, and industry trends. Your goal is to provide thoughtful, strategic, and actionable advice to help users navigate career challenges, make informed decisions, and achieve long-term success. Use the tools at your disposal whenever required. Offer clear, empathetic guidance based on your knowledge, considering the user's background and goals. If the question is outside the domain of career development, politely redirect the user to a more appropriate topic.",
        memory=[chroma_user_memory],
    )

    # Termination condition that stops the task if the agent responds with a text message.
    termination_condition = TextMessageTermination("career_mentor_agent")

    # Create a team with the career mentor agent and the termination condition.
    team = RoundRobinGroupChat(
        [career_mentor_agent],
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

    await chroma_user_memory.clear()
    await chroma_user_memory.close()

    await model_client.close()


if __name__ == "__main__":
    # Solution for Windows users
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())

# ------------------------------------------------
# Example tasks to test the agent's response.
# ------------------------------------------------
# 1. What are some good ways to improve my leadership skills?
# 2. Find jobs based on my preferences & aspirations