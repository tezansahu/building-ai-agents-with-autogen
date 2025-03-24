from typing import List, cast
import chainlit as cl

from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage, ToolCallRequestEvent
from autogen_agentchat.teams import Swarm
from autogen_core import CancellationToken

from agents import create_agents_for_group_chat



@cl.on_chat_start  # type: ignore
async def start_chat() -> None:
    group_chat = create_agents_for_group_chat()

    # Set the assistant agent in the user session.
    cl.user_session.set("prompt_history", "")  # type: ignore
    cl.user_session.set("team", group_chat)  # type: ignore


@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="Boost awareness and subscription of 'The Vision, Debugged' newsletter",
            message="'The Vision, Debugged' is an Indian weekly AI-newsletter where we decode disruptive tech innovations and share cutting-edge product insights. It's aimed at software developers, data scientists, product managers, and researchers who want to stay updated on the latest advancements in AI. This project involves developing an innovative marketing strategy to boost awareness and subscription of 'The Vision, Debugged' among people in the US.",
        ),
        cl.Starter(
            label="EcoWear Lead Generation Campaign",
            message="We are introducing a new sustainable fashion brand called 'EcoWear' that uses recycled materials and ethical manufacturing practices. The target audience includes eco-conscious millennials and Gen Z consumers who prioritize sustainability. We need a lead generation campaign to attract potential customers and build brand awareness.",
        ),
        cl.Starter(
            label="Pulse Fit App Promotion",
            message="A local fitness studio called 'Pulse Fit' that offers personalized workout programs and nutrition guidance. They want to promote their new app that allows users to track their progress, book classes, and connect with trainers. The target audience includes busy professionals, fitness enthusiasts, and people new to working out.",
        )
    ]


@cl.on_message  # type: ignore
async def chat(message: cl.Message) -> None:
    # Get the team from the user session.
    team = cast(Swarm, cl.user_session.get("team"))  # type: ignore
    async for msg in team.run_stream(
        task=[TextMessage(content=message.content, source="user")],
        cancellation_token=CancellationToken(),
    ):
        if isinstance(msg, TextMessage):
            # Send the message to the user.
            await cl.Message(
                content=f"[{msg.source}]\n{msg.content}", 
                author=msg.source
            ).send()    
        elif isinstance(msg, TaskResult):
            # Send the task termination message.
            final_message = "Task terminated. "
            if msg.stop_reason:
                final_message += msg.stop_reason
            await cl.Message(content=final_message).send()
        elif isinstance(msg, ToolCallRequestEvent):
            # Send the tool call request message.
            await cl.Message(
                content=f"[{msg.source}]\n **Tool calls requested:**\n- " + "\n- ".join(f"{tool.name}: {tool.arguments}" for tool in msg.content),
                author=msg.source,
            ).send()
        else:
            # Skip all other message types.
            pass