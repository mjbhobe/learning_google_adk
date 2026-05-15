# Basic ADK Agent

This example introduces the simplest possible agent you can build with the Google Agent Development Kit (ADK). The `basic_agent` is a single-file `LlmAgent` with no tools — it relies entirely on the LLM's pre-trained knowledge to answer questions.

When you first connect, the agent greets you, asks for your name, and then addresses you by name throughout the conversation.

## What is an LlmAgent?

`LlmAgent` (also aliased as `Agent`) is the core building block in ADK. It wraps a Large Language Model and gives it:

- A **name** and **description** so other agents can identify it
- An **instruction** (system prompt) that shapes its personality and behaviour
- An optional list of **tools** that extend what it can do beyond the LLM's built-in knowledge

This example uses none of the optional extras — just a model, a name, and an instruction — making it the ideal starting point.

## Getting Started

### Setup

1. Activate the virtual environment from the root directory:

```bash
# macOS/Linux:
source ../.venv/bin/activate
# Windows CMD:
..\.venv\Scripts\activate.bat
# Windows PowerShell:
..\.venv\Scripts\Activate.ps1
```

1. Create a `.env` file inside the `basic_agent` folder (copy from `.env.example` if present) and add your API key:

```
OPENAI_API_KEY=your_api_key_here
# or
GOOGLE_API_KEY=your_api_key_here
# or
ANTHROPIC_API_KEY=your_api_key_here
```

### Choosing a Model

The agent is pre-configured to use OpenAI via `LiteLlm`. To switch providers, edit [basic_agent/agent.py](basic_agent/agent.py) and update the `model` line:

```python
# OpenAI
model = LiteLlm(model="openai/gpt-5-nano")
# Google Gemini
model = LiteLlm(model="gemini/gemini-3.1-flash-lite")
# Anthropic Claude
model = LiteLlm(model="anthropic/claude-haiku-4-5")
```

See the [LiteLLM provider list](https://docs.litellm.ai/docs/providers) for all supported models.

## Running the Example

(**NOTE:** `$>` denotes the command prompt — don't type this!)

```bash
$> cd 01-basic-agent
$> adk run basic_agent
```

for an interactive terminal session, or:

```bash
$> cd 01-basic-agent
$> adk web
```

to launch the browser-based chat UI (then select **basic_agent** from the dropdown).

Press `Ctrl+C` to exit.

## Example Questions to Try

Because this agent has no external tools, it answers from its pre-trained knowledge. Here are some questions to get you started:

- "What is the capital of Australia?"
- "Explain the difference between TCP and UDP in simple terms."
- "What are the main differences between Python lists and tuples?"
- "Give me a brief history of the internet."
- "What is photosynthesis and why is it important?"
- "Suggest three tips for writing cleaner code."
- "What is the Fibonacci sequence?"

## Additional Resources

- [ADK LlmAgent Documentation](https://google.github.io/adk-docs/agents/llm-agents/)
- [LiteLLM Providers](https://docs.litellm.ai/docs/providers)
