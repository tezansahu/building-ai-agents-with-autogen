import os
import sys
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import asyncio
import json
import requests

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential

from firecrawl import FirecrawlApp

load_dotenv(os.path.join("..", ".env"))

def scrape_website(url: str) -> str:
    """
    Scrape the website content from the given URL.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        str: The scraped content from the website as markdown
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = app.scrape_url(url=url, params={'formats': [ 'markdown' ], 'removeBase64Images': True})
    try:
        return response["markdown"][:20000]
    except KeyError:
        return f"Error: {response}"



def schedule_twitter_thread(thread_plan: str) -> Optional[Dict[str, Any]]:
    """
    Schedule a tweet thread using the given model and time.

    Args:
        thread_plan (str): The JSON string containing the thread plan.

    Returns:
        str: Confirmation message of the scheduled tweet.
    """
    API_URL = "https://api.typefully.com/v1/drafts/"
    HEADERS = {
        "X-API-KEY": f"Bearer {os.getenv('TYPEFULLY_API_KEY')}"
    }

    try:
        thread_json = json.loads(thread_plan)

        print("######## Thread JSON: ", thread_json)
        
        # Convert to Typefully format
        tweets = thread_json['tweets']
        formatted_tweets = []
        for tweet in tweets:
            tweet_text = tweet['content']
            if 'media_urls' in tweet and tweet['media_urls']:
                tweet_text += f"\n{tweet['media_urls'][0]}"
            formatted_tweets.append(tweet_text)
        
        # You can split into multiple tweets by adding 4 consecutive newlines between tweets in the content.
        thread_content = '\n\n\n\n'.join(formatted_tweets)
        
        # Schedule the thread
        payload = {
            "content": thread_content,
            "schedule-date": "next-free-slot"
        }

        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


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

    blog_analyzer = AssistantAgent(
        name="blog_analyzer",
        model_client=model_client,
        # tools=[read_from_file],
        tools=[scrape_website],
        reflect_on_tool_use=True,
        system_message="""You are a technical writer with years of experience writing, editing and reviewing technical blogs. You have a talent for understanding and documenting technical concepts. Your job is to scrape the content of a blog from the given URL & then analyze its contents to create a developer-focused technical overview
        1. Map out the core idea that the blog discusses
        2. Identify key sections and what each section is about
        3. For each section, extract all URLs that appear inside image markdown syntax ![](image_url)
        4. You must associate these identified image urls to their correspoinding sections, so that we can use them with the tweets as media pieces
        Focus on details that are important for a comprehensive understanding of the blog.
        
        The expected output from you is a technical analysis containing:
        - Blog title and core concept/idea
        - Key technical sections identified with their main points
        - Important code examples or technical concepts covered
        - Key takeaways for developers
        - Relevant urls to media that are associated with the key sections and can be associated with a tweet, this must be done
        """,
    )

    twitter_thread_planner = AssistantAgent(
        name="twitter_thread_planner",
        model_client=model_client,
        system_message="""You are a technical writer with years of experience in converting long technical blogs into Twitter threads. You have a talent for breaking longform content into bite-sized tweets that are engaging and informative. And identify relevant urls to media that can be associated with a tweet. 
        
        Your goal is to create a Twitter thread plan based on the provided draft analysis. The thread should break down complex technical concepts into digestible, tweet-sized chunks.

        The plan should include:
        - A strong hook tweet that captures attention, it should be under 10 words, it must be same as the title of the blog
        - Logical flow from basic to advanced concepts
        - Code snippets or key technical highlights that fit Twitter's format
        - Relevant urls to media that are associated with the key sections and must be associated with their corresponding tweets
        - Clear takeaways for engineering audience

        Focus on creating a narrative that technical audiences will find valuable while keeping each tweet concise, accessible and impactful.

        
        The expected output from you is a Twitter thread with tweets in the following JSON format:
        {
            "topic": <A catchy title>,
            "tweets": [
                {
                    "content": <content of the tweet>,
                    "is_hook": <true if the tweet is a hook tweet, false otherwise>
                    "media_urls": [<urls to media that are associated with the tweet, whenever possible>]
                },
                {
                    "content": <content of the tweet>,
                    "is_hook": <true if the tweet is a hook tweet, false otherwise>
                    "media_urls": [<urls to media that are associated with the tweet, whenever possible>]
                },
                ...
            ]
        }
        """,
    )

    tweet_scheduler = AssistantAgent(
        name="tweet_scheduler",
        model_client=model_client,
        tools=[schedule_twitter_thread],
        reflect_on_tool_use=True,
        system_message="""You are a social media manager with years of experience in scheduling tweets. Your task is to schedule the tweets for the given Twitter thread plan. Use the tools at your disposal to accomplish this. Once the tweets are scheduled, reply with 'TERMINATE'""",
    )

    # Terminate the conversation if the tweet scheduler agent mentions "TERMINATE" or if the conversation exceeds 4 messages (1 round)
    termination_condition = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=4) 

    team = RoundRobinGroupChat(
        [blog_analyzer, twitter_thread_planner, tweet_scheduler],
        termination_condition=termination_condition,
    )


    # Run the agent and stream the messages to the console.
    
    task = input("Enter the blog URL: ")
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
# 1. https://nmn.gl/blog/ai-and-learning
# 2. https://huyenchip.com/2025/01/07/agents.html