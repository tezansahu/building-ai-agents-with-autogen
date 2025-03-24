"""
- Product Manager
- User Proxy
- Senior Software Architect
- UI/UX Designer
- Security Specialist
- Report Writer
"""

import os
import sys
from dotenv import load_dotenv
import asyncio
import uuid

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.azure import AzureAIChatCompletionClient
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

    system_analyst = AssistantAgent(
        name="system_analyst",
        description = "A system analyst who ensures a complete understanding of system requirements before proceeding with design.",
        model_client=model_client,
        system_message="You are a thorough system analyst who ensures a complete understanding of system requirements before proceeding with design. You are proficient in asking the right 2-3 questions to understand the functional & non-functional requirements of a problem, as well as summarize them. You **must** reply 'TERMINATE' when you have all the required information for the system.",
    )

    user_proxy = UserProxyAgent(
        name = "user_proxy",
        description = "A user proxy who represents the user's needs and preferences.",
        input_func=input
    )

    senior_software_architect = AssistantAgent(
        name="senior_software_architect",
        description = "A senior software architect who designs the high-level architecture of the system",
        model_client=model_client,
        system_message="You are a skilled software architect who creates robust and scalable high-level system architectures. You have deep knowledge of large-scale systems, focusing on the 'why' behind various design decisions by evaluating tradeoffs effectively. You are also an expert in representing complex system in easy-to-understand diagrams with Mermaid. You also have a solid understanding of data storage technologies & system interface design. You must create a robust, scalable high-level design of the software based on the requirement (with an architcture diagram), the tradeoffs considered while arriving at the design, along with the potential tech stack. Optimize for brevity. Do NOT suggest anything beyond your expertise.",
    )

    uiux_expert = AssistantAgent(
        name="uiux_expert",
        description = "A UI/UX expert who designs the user interface and experience.",
        model_client=model_client,
        system_message="You are a UI/UX expert who designs user interfaces and experiences. You are aware of the best practices of design thinking & are proficient in creating user-friendly designs that enhance usability and accessibility. You must build on the previous discussion & create intuitive, accessible interfaces for the system that enhance user experience. You must Optimize for brevity. Do NOT suggest anything beyond your expertise.",
    )

    security_specialist = AssistantAgent(
        name="security_specialist",
        description = "A security specialist who ensures the system is secure.",
        model_client=model_client,
        system_message="You are a security specialist who ensures the system is secure. You are proficient in identifying potential vulnerabilities and suggesting best practices for securing systems. You have expertise in authentication, authorization, encryption, and secure communication protocols, and can design security monitoring and incident response mechanisms. You must build on the previous discussion & identify vulnerabilities and suggest security measures throughout the system design. Optimize for brevity. Do NOT suggest anything beyond your expertise.",
    )

    devops_engineer = AssistantAgent(
        name="devops_engineer",
        description = "A DevOps engineer who ensures the system is deployable and maintainable.",
        model_client=model_client,
        system_message="You are a DevOps engineer who designs for operability, reliability, and maintainability. You are proficient in CI/CD practices, infrastructure as code, and monitoring systems. You bring expertise in containerization, orchestration, and cloud technologies, ensuring systems are designed with scalability, fault tolerance, and observability in mind from the beginning. You must build on the previous discussion & suggest the most optimal deployment, maintenance & telemetry strategies for the system. Optimize for brevity. Do NOT suggest anything beyond your expertise.",
    )

    planning_agent = AssistantAgent(
    "planning_agent",
    description="An agent for planning tasks and delegating them to other agents. This agent must be called first",
    model_client=model_client,
    system_message="""
    You are a planning agent.
    Your job is to break down complex tasks into smaller, manageable subtasks.
    Your team members are:
    - senior_software_architect: A senior software architect who designs the high-level architecture of the system.
    - uiux_expert: A UI/UX expert who designs the user interface and experience.
    - security_specialist: A security specialist who ensures the system is secure.
    - devops_engineer: A DevOps engineer who ensures the system is deployable and maintainable.
    - report_writer: A report writer who writes the final report or software design document.

    You only plan and delegate tasks - you do not execute them yourself.

    When assigning tasks, use this format:
    1. <agent> : <task>

    """,
)

    report_writer = AssistantAgent(
        name="report_writer",
        description = "A report writer who writes the final report or software design document.",
        model_client=model_client,
        system_message="You are an experienced technical report writer, proficient in consolidating deep technical discussions into well-structured & articulare design documents. Respond by consolidating the entire deep technical discussion into well-structured & articulate design document in markdown format and end the response with 'TERMINATE'",
    )

    requirments_team = RoundRobinGroupChat(
        [system_analyst, user_proxy],
        termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=4)
    )

    task = input("What kind of system do you wish to design? ")
    requirements = await Console(requirments_team.run_stream(task=task))

    software_design_task =  f"Design a {task} with the following requirements:\n{requirements.messages[-1].content.strip('TERMINATE').strip()}"


    selector_prompt = """Select an agent to perform task.

{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from {participants} to perform the next task.
Stick to the original plan created by the planning agent when selecting an agent.
Only select one agent.
"""


    # Terminate the conversation if the tweet scheduler agent mentions "TERMINATE" or if the conversation exceeds 10 messages
    termination_condition = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=25)

    software_design_team = SelectorGroupChat(
        [
            planning_agent,
            senior_software_architect,
            uiux_expert,
            security_specialist,
            devops_engineer,
            report_writer
        ],
        model_client=model_client,
        selector_prompt=selector_prompt,
        termination_condition=termination_condition,
    )

    result = await Console(software_design_team.run_stream(task=software_design_task))

    # Write to a file
    id = str(uuid.uuid4())
    with open(f"system_design_report_{id}.md", "w") as f:
        f.write(result.messages[-1].content.strip("TERMINATE").strip())
    
    await model_client.close()


if __name__ == "__main__":
    # Solution for Windows users
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())

# ------------------------------------------------
# Example tasks to test the agent's response.
# ------------------------------------------------
# 1. https://nmn.gl/blog/ai-and-learning
# 2. https://huyenchip.com/2025/01/07/agents.html