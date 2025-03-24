from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import Swarm
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential

from tools import *

def create_agents_for_group_chat() -> Swarm:
    """
    Create a group chat with agents for the given task.
    """
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

    # Create the agents
    lead_marketing_analyst = AssistantAgent(
        name="lead_marketing_analyst",
        model_client=model_client,
        tools=[serper_web_search, scrape_website],
        system_message="""As the Lead Market Analyst at a premier digital marketing firm, you specialize in dissecting online business landscapes.

        Your goal is to conduct amazing analysis of the products and competitors, providing in-depth insights to guide marketing strategies.

        Based on the customer's project description, conduct a thorough research about the customer and competitors in the context of the customer's domain. Make sure you find any interesting and relevant information given the current year is 2025.

        Your analysis **must** include a complete report on the customer and their competitors, including their demographics, preferences, market positioning and audience engagement.

        Once you have all the information, you **must** first send your message. 
        """,
        handoffs=["chief_marketing_strategist"],
    )

    chief_marketing_strategist = AssistantAgent(
        name="chief_marketing_strategist",
        model_client=model_client,
        system_message="""You are the Chief Marketing Strategist at a leading digital marketing agency, known for crafting bespoke strategies that drive success. 
        
        Your goal is to synthesize amazing insights from product analysis to formulate incredible marketing strategies.
        Understand the project details and the target audience for the customer's project. Review any provided materials and gather additional information as needed.

        **Task 1:**
        First, create a detailed summary of the project and a profile of the target audience.

        **Task 2:**
        Next, formulate a comprehensive marketing strategy for the project of the customer. Use the insights from the research and the project summary to create a high-quality strategy. This must be a detailed marketing strategy document that outlines the goals, target audience, key messages, and proposed tactics, make sure to have name, tatics, channels and KPIs. 
        
        **You must first send your message after completing the tasks.** 
        """,
        handoffs=["creative_content_creator"],
    )

    creative_content_creator = AssistantAgent(
        name="creative_content_creator",
        model_client=model_client,
        tools=[serper_web_search, scrape_website],
        system_message="""As a Creative Content Creator at a top-tier digital marketing agency, you excel in crafting narratives that resonate with audiences. Your expertise lies in turning marketing strategies into engaging stories and visual content that capture attention and inspire action.

        Your goal is to develop compelling and innovative content for social media campaigns, with a focus on creating high-impact ad copies.
        
        **Task 1:**
        Develop creative marketing campaign ideas for the customer's project. Ensure the ideas are innovative, engaging, and aligned with the overall marketing strategy. Send a message containing a list of 5 campaign ideas, each with the following details:
        - Campaign Name
        - Description
        - Target Audience
        - Channel
        - Expected Impact

        **Task 2:**
        Next, create marketing copies based on the campaign ideas. Ensure the copies are compelling, clear, and tailored to the target audience. The marketing copies for each campaign idea must have a title & a body.

        Reply with TERMINATE when you are done with the tasks.
        """,
    )

    # Create the group chat
    group_chat = Swarm(
        [lead_marketing_analyst, chief_marketing_strategist, creative_content_creator],
        termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=10)
    )

    return group_chat