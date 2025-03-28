# UI for AI Agents

This folder contains implementations of user interfaces for AI agents, showcasing how agents can interact with users through a UI. 

The scripts in this folder leverage `Chainlit` to create interactive chat interfaces for multi-agent systems.

## Contents

1. **[tools.py](tools.py)**
   Defines the tools to be used by the agents
   - Web Search Tool 
   - Web Scraper Tool

2. **[agents.py](agents.py)**  
   Defines the agents and their roles for group chat interactions.  
   - **Lead Marketing Analyst**: Conducts competitor analysis and provides insights.  
   - **Chief Marketing Strategist**: Crafts marketing strategies based on analysis.  
   - **Creative Content Creator**: Generates compelling marketing content.

3. **[app.py](app.py)**  
   Implements the Chainlit-based UI for interacting with the agents.  
   - Allows users to start a chat session with the agents.  
   - Handles user messages and displays agent responses in real-time.

## Prerequisites

Ensure you have the following installed:
- Python 3.10 or higher
- Required dependencies listed in the [requirements.txt](../0-Environment-Setup/requirements.txt)

To install the dependencies, run:
```bash
pip install -r [requirements.txt](../0-Environment-Setup/requirements.txt)
```

## To Run the Agent

1. Navigate to this folder:
   `cd 3-UI-For-AI-Agents`

2. Start the Chainlit server to launch the UI:
   `chainlit run app.py`

3. Open the URL provided in the terminal (usually http://localhost:8000) to access the UI.

4. Interact with the agents through the chat interface.