# Building AI Agents with AutoGen

This repository demonstrates the implementation of AI agents using the AutoGen framework, to accompany the workshop "Building AI Agents with AutoGen".

It showcases various single-agent and multi-agent systems, as well as a user interface for interacting with these agents. Each system is designed to solve specific tasks, ranging from career mentoring to collaborative system design and marketing campaign creation.

## Project Structure

The project is organized into the following directories:

1. **[0-Environment-Setup](0-Environment-Setup/)**  
   Contains setup instructions, dependencies, and environment configuration files.

2. **[1-Single-Agent-System](1-Single-Agent-System/)**  
   Demonstrates the capabilities of single-agent systems with various enhancements like tools, memory, and retrieval-augmented generation (RAG).

3. **[2-Multi-Agent-System](2-Multi-Agent-System/)**  
   Implements collaborative multi-agent systems for complex tasks like system design, marketing campaigns, and code review.

4. **[3-UI-For-AI-Agents](3-UI-For-AI-Agents/)**  
   Provides a user interface for interacting with AI agents using Chainlit.

5. **[ai-agents](ai-agents/)**  
   Contains shared utilities and modules for the agents.

---

## Agents Overview

### Single-Agent Systems
Single-agent systems demonstrate the capabilities of individual agents in solving specific tasks.

1. **[1.1-basic-single-agent.py](1-Single-Agent-System/1.1-basic-single-agent.py)**  
   A basic implementation of a single-agent system with a predefined persona.

2. **[1.2-single-agent-with-tools.py](1-Single-Agent-System/1.2-single-agent-with-tools.py)**  
   Enhances the agent with tools like web search and report writing for improved functionality.

3. **[1.3-single-agent-team.py](1-Single-Agent-System/1.3-single-agent-team.py)**  
   Implements a single agent capable of executing tasks in a self-looping manner.

4. **[1.4-single-agent-team-with-memory.py](1-Single-Agent-System/1.4-single-agent-team-with-memory.py)**  
   Adds memory capabilities to the agent for better context retention across interactions.

5. **[1.5-single-agent-team-with-RAG.py](1-Single-Agent-System/1.5-single-agent-team-with-RAG.py)**  
   Integrates retrieval-augmented generation (RAG) for enhanced information retrieval and generation.

---

### Multi-Agent Systems
Multi-agent systems showcase collaboration between multiple agents to solve complex tasks.

1. **[2.1-reflection-coder-reviewer.py](2-Multi-Agent-System/2.1-reflection-coder-reviewer.py)**  
   A coder-reviewer system where one agent writes code, and another reviews and validates it.

2. **[2.2-sequential-blog-to-tweet-thread-scheduler.py](2-Multi-Agent-System/2.2-sequential-blog-to-tweet-thread-scheduler.py)**  
   Converts a blog into a Twitter thread and schedules it for posting using three agents:
   - Blog Analyzer
   - Twitter Thread Planner
   - Tweet Scheduler

3. **[2.3-planning-with-HiTL-system-design.py](2-Multi-Agent-System/2.3-planning-with-HiTL-system-design.py)**  
   A human-in-the-loop (HiTL) system design agent that collaborates with specialized agents to create a system design document. Agents include:
   - Planning Agent
   - System Analyst
   - Senior Software Architect
   - UI/UX Specialist
   - Security Specialist
   - DevOps Engineer
   - Report Writer

4. **[2.4-swarm-marketing-campaign-creator.py](2-Multi-Agent-System/2.4-swarm-marketing-campaign-creator.py)**  
   A swarm-based system where agents collaborate to create a comprehensive marketing campaign. Agents include:
   - Lead Marketing Analyst
   - Chief Marketing Strategist
   - Creative Content Creator

---

### UI for AI Agents
The **[3-UI-For-AI-Agents](3-UI-For-AI-Agents/)** directory provides a Chainlit-based user interface for interacting with the agents.

1. **[tools.py](3-UI-For-AI-Agents/tools.py)**  
   Defines tools like web search and web scraping for use by the agents.

2. **[agents.py](3-UI-For-AI-Agents/agents.py)**  
   Defines agents for group chat interactions:
   - Lead Marketing Analyst
   - Chief Marketing Strategist
   - Creative Content Creator

3. **[app.py](3-UI-For-AI-Agents/app.py)**  
   Implements the Chainlit-based UI for interacting with the agents in real-time.

---