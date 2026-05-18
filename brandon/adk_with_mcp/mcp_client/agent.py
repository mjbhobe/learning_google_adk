"""
ADK Agent interfacing with a local MCP server.
Mirrors the LangChain-based agent in 01_mcp.ipynb.

The agent's instruction is fetched from the local MCP server's @mcp.prompt() at startup.
Tools:
  - web_search  : fetched via McpToolset from the local MCP server (MCP tool)
  - github_file : ADK function tool replicating the MCP server's @mcp.resource()

Run with:
    adk web          (from the brandon/adk_with_mcp/ directory)
    adk run mcp_client

@Author: Manish Bhobé
My experiments with AI/Gen AI. Code shared for learning purposes only.
Use at your own risk!!
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp import StdioServerParameters
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams

load_dotenv(override=True)

# Windows: MCP stdio transport spawns subprocesses, which require ProactorEventLoop.
# Without this, asyncio raises NotImplementedError on Windows when launching stdio servers.
if sys.platform == "win32":
    if not isinstance(
        asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy
    ):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

MCP_SERVER_PATH = str(Path(__file__).parent / "resources" / "local_mcp_server.py")

_FALLBACK_INSTRUCTION = """\
You are a helpful assistant that answers questions about LangChain, LangGraph and LangSmith.

You can use the following tools to answer user's questions:
- web_search: search the web for information.
- github_file: access the langchain-ai/langchain-mcp-adapters README file.

If the user asks a question NOT RELATED to LangChain, LangGraph or LangSmith, respond with:
"I am sorry, I can only answer questions related to LangChain, LangGraph and LangSmith.\
 Please ask a relevant question."

You may try multiple tool calls to answer the user's question and may ask clarifying\
 questions first.
"""


def _run_async_safely(coro):
    """Run a coroutine synchronously, compatible with already-running loops (e.g. Jupyter)."""
    try:
        asyncio.get_running_loop()
        # An event loop is already running — spin up a fresh thread with its own loop
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result(timeout=60)
    except RuntimeError:
        # No running loop — safe to call asyncio.run() directly
        return asyncio.run(coro)


async def _fetch_mcp_instruction() -> str:
    """Connect to the local MCP server and retrieve its @mcp.prompt() text."""
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[MCP_SERVER_PATH],
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_prompts()
                if result.prompts:
                    prompt_result = await session.get_prompt(result.prompts[0].name)
                    if prompt_result.messages:
                        content = prompt_result.messages[0].content
                        return content.text if hasattr(content, "text") else str(content)
    except Exception as exc:
        print(f"[agent] Warning: could not fetch MCP prompt — using fallback. ({exc})")
    return _FALLBACK_INSTRUCTION


def github_file() -> str:
    """Access the langchain-ai/langchain-mcp-adapters README.md from the GitHub repository.

    Replicates the MCP server's @mcp.resource("github://langchain-ai/...") by fetching
    the same raw GitHub URL that the resource handler uses.
    """
    from requests import get

    url = "https://raw.githubusercontent.com/langchain-ai/langchain-mcp-adapters/main/README.md"
    try:
        response = get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as exc:
        return f"Error fetching GitHub file: {exc}"


# Fetch the system instruction from the MCP server once at import time
_instruction = _run_async_safely(_fetch_mcp_instruction())

root_agent = LlmAgent(
    model=LiteLlm(model="openai/gpt-5-nano"),
    name="langchain_helper",
    description="Assistant for LangChain, LangGraph and LangSmith questions",
    instruction=_instruction,
    tools=[
        # web_search comes from the MCP server via the stdio transport
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=[MCP_SERVER_PATH],
                ),
                timeout=30.0,
            ),
        ),
        # github_file replicates the MCP server's @mcp.resource() as a direct ADK tool
        github_file,
    ],
)
