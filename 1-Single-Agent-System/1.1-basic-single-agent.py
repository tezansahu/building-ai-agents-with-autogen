import os
import sys
from dotenv import load_dotenv
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.azure import AzureAIChatCompletionClient
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential


load_dotenv(os.path.join("..", ".env"))



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



    # Define an AssistantAgent with the model & system message
    # The system message instructs the agent via natural language.
    career_mentor_agent = AssistantAgent(
        name="career_mentor_agent",
        model_client=model_client,
        system_message="You are a Career Mentor Agent with deep expertise in career development, professional growth, and industry trends. Your goal is to provide thoughtful, strategic, and actionable advice to help users navigate career challenges, make informed decisions, and achieve long-term success. Offer clear, empathetic guidance based on your knowledge, considering the user's background and goals. If the question is outside the domain of career development, politely redirect the user to a more appropriate topic.",
        model_client_stream=True,  # Enable streaming tokens from the model client.
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
# 1. I'm a college student studying computer science, but I'm not sure what career path to follow.  # Related to career development.
# 2. What are the best practices making my resume stand out from the crowd?                         # Related to career development.
# 3. What is the weather today in Bangalore?                                                        # Not related to career development.
# 4. Can you help me figure out what options might suit my skills and interests?                    # Related to career development - multi-turn expected