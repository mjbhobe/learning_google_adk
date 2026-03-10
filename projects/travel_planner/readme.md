# ADK-Powered Travel Planner 🌍🛫

This project is a multi-agent AI-powered travel planner built using Google's Agent Development Kit (ADK). It showcases how intelligent agents can coordinate to plan a complete trip: flights, stays, and activities. A simple Streamlit UI wraps everything for an intuitive end-user experience.

## 📚 What is ADK?

ADK (Agent Development Kit) is Google's open-source framework designed to help developers build modular, production-ready multi-agent systems powered by LLMs. It supports:

Hierarchical, parallel, or sequential agent orchestration

Integration with models via LiteLLM: GPT-4o, Claude, Gemini, Mistral, etc.

Streaming conversations, callbacks, session memory

Deployment in any environment (local, container, or cloud)

Each agent in ADK is self-contained, exposing a /run endpoint and metadata for discovery using the A2A (Agent-to-Agent) protocol.

## 🎨 Project Overview

This travel planner demonstrates a modular, orchestrated agent workflow:

User Input → Streamlit UI → Host Agent → [Flight Agent, Stay Agent, Activities Agent]

host_agent: Coordinates the planning process

flight_agent: Suggests flights

stay_agent: Recommends hotels

activities_agent: Suggests local experiences

Agents communicate over REST using FastAPI and respond with structured JSON outputs.

## 📂 Project Structure

ADK_demo/

├── agents/

│   ├── host_agent/

│   ├── flight_agent/

│   ├── stay_agent/

│   └── activities_agent/

├── shared/           # Shared Pydantic models

├── common/           # A2A client/server logic

├── streamlit_app.py  # UI

├── requirements.txt

└── README.md

## 🚀 Getting Started

1. Setup Environment
```
python3 -m venv adk_demo
source adk_demo/bin/activate
pip install -r requirements.txt
```

Add your OpenAI/Gemini API key:

```
export OPENAI_API_KEY="your-api-key"
```

## 🔄 Run the Agents and UI

Start each agent using the following commands in terminal :

```
uvicorn agents.host_agent.__main__:app --port 8000 &
uvicorn agents.flight_agent.__main__:app --port 8001 &
uvicorn agents.stay_agent.__main__:app --port 8002 &
uvicorn agents.activities_agent.__main__:app --port 8003 &
```

Launch the frontend:

```
streamlit run streamlit_app.py
```

## 🤖 Contributing

Contributions are welcome! Please open issues or submit PRs with improvements.