import os
import sys
import requests
import json
from dotenv import load_dotenv
import asyncio

from autogen_agentchat.agents import AssistantAgent
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
        with open(filename, "w") as file:
            file.write(content)
        return f"Report written to: {filename}"
    except Exception as e:
        return f"Error: {str(e)}"

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

    # Define an AssistantAgent with the model, tools & system message
    # The system message instructs the agent via natural language.
    career_mentor_agent = AssistantAgent(
        name="career_mentor_agent",
        model_client=model_client,
        tools=[serper_web_search, write_report],
        reflect_on_tool_use=True,
        system_message="You are a Career Mentor Agent with deep expertise in career development, professional growth, and industry trends. Your goal is to provide thoughtful, strategic, and actionable advice to help users navigate career challenges, make informed decisions, and achieve long-term success. Use the tools at your disposal whenever required. Offer clear, empathetic guidance based on your knowledge, considering the user's background and goals. If the question is outside the domain of career development, politely redirect the user to a more appropriate topic.",
    )

    # Run the agent and stream the messages to the console.

    task = input("Enter your task: ")  # Get the user input for the task.

    # For single-turn conversation, you can use the following code:
    await Console(career_mentor_agent.run_stream(task=task))

    # # For multi-turn conversation, you can use the following code:
    # while True:
    #     stream = career_mentor_agent.run_stream(task=task)
    #     await Console(stream)

    #     # Get the user response.
    #     task = input("\nContinue the conversation (type 'exit' to leave): ")
    #     if task.lower().strip() == "exit":
    #         break

    await model_client.close()


if __name__ == "__main__":
    # Solution for Windows users
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())


# ------------------------------------------------
# Example tasks to test the agent's response.
# ------------------------------------------------
# 1. What are the latest trends in the tech industry in 2025?
# 2. Write a report on fresher salaries at Amazon, Google & Microsoft India for SDEs & save it to a file.     # Does NOT write to file.