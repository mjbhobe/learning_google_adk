# ADK Agent with Local MCP Server

A Google ADK agent powered by OpenAI `gpt-5-nano` that uses tools sourced from a
local [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server.
This is the ADK equivalent of the LangChain-based agent in `01_mcp.ipynb`.

---

## What this app does

```
┌─────────────────────────────────────────────────────────────────┐
│  User (browser / terminal)                                      │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐   instruction (fetched at startup)            │
│  │  ADK Agent  │◄──────────────────────────────────────────┐   │
│  │  (LlmAgent) │                                           │   │
│  │  gpt-5-nano │                                           │   │
│  └──────┬──────┘                                           │   │
│         │  tool calls                                      │   │
│         ▼                                                  │   │
│  ┌──────────────────────────────────────────┐  ┌─────────┐│   │
│  │  McpToolset  (stdio subprocess)          │  │ MCP     ││   │
│  │  └─► web_search (Tavily web search)      │  │ Server  ││   │
│  └──────────────────────────────────────────┘  │ @prompt ││   │
│                                                └─────────┘│   │
│  ┌───────────────────────────────────────────┐            │   │
│  │  github_file (direct ADK function tool)   │────────────┘   │
│  │  └─► fetches langchain-mcp-adapters README│                │
│  └───────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

The agent specialises in answering questions about **LangChain**, **LangGraph**,
and **LangSmith**.  It uses two tools:

| Tool | Source | What it does |
|---|---|---|
| `web_search` | MCP server `@mcp.tool()` | Searches the web via Tavily |
| `github_file` | MCP server `@mcp.resource()` (wrapped as ADK tool) | Fetches the `langchain-mcp-adapters` README from GitHub |

The agent's **system instruction** is also pulled from the MCP server's
`@mcp.prompt()` function at startup, so the agent's persona is fully controlled
by the MCP server.

---

## How the MCP server is launched (you don't start it manually)

The local MCP server (`resources/local_mcp_server.py`) uses the **`stdio`
transport** — it communicates over `stdin`/`stdout`.  ADK's `McpToolset` with
`StdioConnectionParams` **automatically spawns the server as a subprocess** the
moment the agent needs a tool.  You never have to start or stop the server
yourself; ADK manages its entire lifecycle.

```
Agent needs web_search
  └─► McpToolset spawns:  python resources/local_mcp_server.py
  └─► Sends JSON-RPC over stdio
  └─► Gets tool result back
  └─► Kills subprocess when done
```

The only thing required is that the Python environment has all dependencies
installed (including `tavily`) and that `TAVILY_API_KEY` is set in `.env`.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python ≥ 3.11 | The project's venv uses 3.14 |
| `OPENAI_API_KEY` | For `gpt-5-nano` via LiteLLM |
| `TAVILY_API_KEY` | For the `web_search` MCP tool |
| All packages installed | See Setup below |

---

## Setup

### 1 — Clone / open the project

This file lives at:
```
learning_google_adk/
  brandon/
    adk_with_mcp/
      mcp_client/          ← you are here
        agent.py
        resources/
          local_mcp_server.py
```

### 2 — Install dependencies

From the **project root** (`learning_google_adk/`):

```bash
# with uv (recommended — this project uses uv)
uv sync

# or with pip
pip install -r requirements.txt
```

If `tavily` is missing (it's a `local_mcp_server.py` dependency):

```bash
uv add tavily
# or
pip install tavily
```

### 3 — Set environment variables

Make sure your `.env` file in the project root contains:

```dotenv
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

> The agent loads `.env` automatically via `python-dotenv`.

---

## Running the agent

Run both commands from the **`brandon/adk_with_mcp/`** directory
(the parent of `mcp_client/`).

### Option A — ADK Web UI (recommended for interactive testing)

```bash
cd brandon/adk_with_mcp
adk web
```

Open `http://localhost:8000` in your browser, select **langchain_helper** from
the agent list, and start chatting.

### Option B — ADK terminal (single turn)

```bash
cd brandon/adk_with_mcp
adk run mcp_client
```

Type your question and press Enter.  Type `exit` to quit.

> **Note (Windows):** The agent already applies `WindowsProactorEventLoopPolicy`
> at startup so stdio-based MCP subprocesses work correctly on Windows.

---

## Example queries

### ✅ Queries the agent will answer (LangChain / LangGraph / LangSmith)

These are on-topic and will trigger tool use before replying:

```
What is LangChain and what problems does it solve?
```
```
How do I build a stateful agent with LangGraph?
```
```
What is the difference between LangChain and LangGraph?
```
```
Tell me about the langchain-mcp-adapters library.
```
```
How does LangSmith help with debugging LLM applications?
```
```
What checkpointers does LangGraph support for persistent memory?
```
```
How do I connect an MCP tool server to a LangChain agent?
```

### ❌ Queries the agent will refuse ("I am sorry..." response)

These are off-topic.  The agent will respond with:
> *"I am sorry, I can only answer questions related to LangChain, LangGraph and
> LangSmith. Please ask a relevant question."*

```
What is the weather in Mumbai today?
```
```
Who is the CEO of OpenAI?
```
```
Write a Python function to sort a list of numbers.
```
```
What is Google ADK?
```
```
What is the latest stock price of Apple?
```
```
Tell me a joke.
```
```
What is the capital of France?
```

---

## Project structure

```
mcp_client/
├── agent.py                  ← ADK root_agent (this is the main file)
├── __init__.py               ← makes this a Python package (required by ADK)
├── README.md                 ← this file
└── resources/
    └── local_mcp_server.py   ← FastMCP server (web_search tool + github_file resource + prompt)
```

### Key design decisions vs. the LangChain notebook

| Aspect | LangChain (`01_mcp.ipynb`) | ADK (`agent.py`) |
|---|---|---|
| MCP client | `MultiServerMCPClient` | `McpToolset` + low-level `ClientSession` |
| `web_search` | tool via MCP adapter | tool via `McpToolset` (stdio subprocess) |
| `github_file` | resource via MCP adapter | direct ADK function tool (same URL) |
| System prompt | `client.get_prompt(...)` | `session.get_prompt(...)` at startup |
| Model | `openai:gpt-5-nano` | `LiteLlm("openai/gpt-5-nano")` |

`github_file` is implemented as a direct ADK function tool (not via `McpToolset`)
because MCP resources are not the same as MCP tools — `McpToolset` only exposes
`@mcp.tool()` items.  The function fetches the identical GitHub URL that the
`@mcp.resource()` handler uses, so the agent's behaviour is equivalent.