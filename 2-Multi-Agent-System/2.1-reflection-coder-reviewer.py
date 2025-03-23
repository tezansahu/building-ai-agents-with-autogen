import os
import sys
from dotenv import load_dotenv
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential

from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.tools.code_execution import PythonCodeExecutionTool


load_dotenv(os.path.join("..", ".env"))


python_code_executor_tool = PythonCodeExecutionTool(
    LocalCommandLineCodeExecutor(work_dir="./code_executor"),
)


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

    coder_agent = AssistantAgent(
        name="coder_agent",
        model_client=model_client,
        # system_message="You are a coding assistant that can help with code-related tasks by writing elgant Python code.",
        system_message="You are a helpful assistant. Write all code in python & get it verified",
    )

    critic_agent = AssistantAgent(
        name="critic_agent",
        model_client=model_client,
        tools=[python_code_executor_tool],
        system_message="You are a code reviewer that can help with code-related tasks by running the code, reviewing it and providing feedback to correct or optimize the code. Respond with 'TERMINATE' only if the code is correct and you have no more feedback.",
        reflect_on_tool_use=True,
    )

    # Terminate the conversation if the critic agent mentions "TERMINATE" or if the conversation exceeds 6 messages (3 rounds)
    termination_condition = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=6) 

    # Create a team with the career mentor agent and the termination condition.
    team = RoundRobinGroupChat(
        [coder_agent, critic_agent],
        termination_condition=termination_condition,
    )

    # Run the agent and stream the messages to the console.
    
    task = input("Enter your task: ")           # Get the user input for the task.
    await Console(team.run_stream(task=task))
    
    await model_client.close()


if __name__ == "__main__":
    # Solution for Windows users
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())

# ------------------------------------------------
# Example tasks to test the agent's response.
# ------------------------------------------------
# 1. Write code to print the Fibonacci sequence
# 2. Implement a solution for the knapsack problem in Python.