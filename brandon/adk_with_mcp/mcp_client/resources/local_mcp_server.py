"""
01_mcp.py: exploring MCP servers with LangChain
"""

from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict, Any
from requests import get

load_dotenv(override=True)


mcp = FastMCP("mcp_server")
tavily_client = TavilyClient()


# tool for searching web using MCP protocol
# NOTE the @mcp.tool() decorator rather than our usual @tool decorator
@mcp.tool()
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information based on query"""
    response = tavily_client.search(query)
    return response


# let's define a resource our agent can use
@mcp.resource("github://langchain-ai/langchain-mcp-adapters/blob/main/README.md")
def github_file():
    """resource for accessing the langchain-ai/langchain-mcp-adapters/README.md file"""
    url = "https://raw.githubusercontent.com/langchain-ai/langchain-mcp-adapters/main/README.md"
    try:
        response = get(url)
        return response.text
    except Exception as e:
        print(f"Error occurred while fetching GitHub file: {e}")
        return f"Error occurred while fetching the file -> {str(e)}"


# define a prompt template
@mcp.prompt()
def prompt():
    """analyze data from langchain-ai repo file with comprehensive insights"""
    return """
    You are a helpful assistant that answers questions about LangChain, LangGraph and LangSmith.
    
    You can use the following tools/resources to answe user's questions:
    - search_web: search the web for information.
    - github_file: Access the langchain-ai repo files.

    If user user asks a question that is NOT RELATED to LangChain, LangGraph or LangSmith, you
    should respond with "I am sorry, I can only answer questions related to LangChain, LangGraph and LangSmith. Please ask a relevant question."

    You may try multiple tools and resource calls to answer the user's question.

    You may also ask clarifying questions to the user to better understand their question before responding.
    """


if __name__ == "__main__":
    mcp.run(transport="stdio")
