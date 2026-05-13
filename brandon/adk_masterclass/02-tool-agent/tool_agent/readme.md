# ADK Agent with tools

This example illustrates how you can use custom tools with an ADK agent to enhance it's capabilities. By deafult, the ADK agent will rely on the underlying model's (such as OpenAI GPT model or Gemini model) training data to generate responses.

Tools enhance capabilities of the LLM - they empower agents to transcend their training data by enabling them to interact with external APIs, execute specialized code, and access private databases to perform real-world actions.

The Google ADK provides a lot of custom tools of it's own, all part of the `google.adk.tools` package:
| Tool | Description |
| :-- | :-- |
| `google_search` | Live web search using Google Search under the hood |

**TODO:** add other in-built tools to above table! 

**Unfortunately, these tools can be used with your ADK agent ONLY if you use Gemini models! **