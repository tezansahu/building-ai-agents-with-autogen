# Agents Assemble! Building Powerful AI Workforces with AutoGen 0.4

This repository demonstrates the implementation of AI agents using the AutoGen 0.4 framework, for the session "Agents Assemble! Building Powerful AI Workforces with AutoGen 0.4", as a part of the 24xAI Conference (2025).

It showcases various single-agent and multi-agent systems, as well as a user interface for interacting with these agents. Each system is designed to solve specific tasks, ranging from career mentoring to collaborative system design and marketing campaign creation.

## Project Structure

The project is organized into the following directories:

1. **[0-Environment-Setup](0-Environment-Setup/)**  
   Contains setup instructions, dependencies, and environment configuration files.

2. **[1-Single-Agent-System](1-Single-Agent-System/)**  
   Demonstrates the capabilities of single-agent systems with various enhancements like tools, memory, and retrieval-augmented generation (RAG).

3. **[2-Multi-Agent-System](2-Multi-Agent-System/)**  
   Implements collaborative multi-agent systems for complex tasks like system design, marketing campaigns, and code review.

---

## Agents Overview

### Single-Agent Systems
Single-agent systems demonstrate the capabilities of individual agents in solving specific tasks.

1. **[1.1-single-agent-with-tools-team.py](1-Single-Agent-System/1.1-single-agent-with-tools-team.py)**  
   Implements a single agent with a persona, equipped with some tools, that can execute with self-looping.

4. **[1.2-single-agent-team-with-memory.py](1-Single-Agent-System/1.2-single-agent-team-with-memory.py)**  
   Adds memory capabilities to the agent for better context retention across interactions.

5. [Optional] **[1.3-single-agent-team-with-RAG.py](1-Single-Agent-System/1.3-single-agent-team-with-RAG.py)**  
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

---