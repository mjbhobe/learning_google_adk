# Lingo Flip Agent

This example builds on the simplest ADK agent pattern to create something a little more fun. `lingo_flip` is a single-file `LlmAgent` with no tools — it uses the LLM's pre-trained knowledge to translate plain English sentences into Gen Z slang, complete with explanations for Boomers, Gen X, and Millennials who might not be in the loop.

## What Does It Do?

Send `lingo_flip` any sentence in plain English and it rewrites it in Gen Z lingo, using phrases like *"no cap"*, *"slay"*, *"it's giving"*, *"lowkey"*, and more. The first time it introduces a new piece of slang it explains what it means — so older generations aren't left scratching their heads.

## What is an LlmAgent?

`LlmAgent` (also aliased as `Agent`) is the core building block in ADK. It wraps a Large Language Model and gives it:

- A **name** and **description** so other agents can identify it
- An **instruction** (system prompt) that shapes its personality and behaviour
- An optional list of **tools** that extend what it can do beyond the LLM's built-in knowledge

`lingo_flip` uses none of the optional extras — just a model, a name, and a carefully crafted instruction — making it a great second step after [basic_agent](../basic_agent/readme.md) for seeing how the system prompt alone can dramatically change an agent's personality.

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

2. Create a `.env` file inside the `lingo_flip` folder (copy from `.env.example` if present) and add your API key:

```
OPENAI_API_KEY=your_api_key_here
# or
GOOGLE_API_KEY=your_api_key_here
# or
ANTHROPIC_API_KEY=your_api_key_here
```

### Choosing a Model

The agent is pre-configured to use OpenAI via `LiteLlm`. To switch providers, edit [lingo_flip/agent.py](agent.py) and update the `model` line:

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
$> adk run lingo_flip
```

for an interactive terminal session, or:

```bash
$> cd 01-basic-agent
$> adk web
```

to launch the browser-based chat UI (then select **lingo_flip** from the dropdown).

Press `Ctrl+C` to exit.

## Example Sentences to Translate

Send the agent any plain English sentence and watch it get a Gen Z makeover:

- "I'm really tired today and don't feel like doing anything."
- "That movie we watched last night was absolutely amazing."
- "I completely agree with everything you just said."
- "She's very confident and stylish — everyone admires her."
- "I honestly have no idea what's going on."
- "This party is really boring; I want to go home."
- "He pretends to be rich but everyone knows the truth."
- "I'm a little nervous about my job interview tomorrow."
- "That outfit you're wearing looks incredible."
- "We should stop overthinking and just do it."

## Project for you
If you loved this example, try doing the reverse - translate Gen-Z lingo to plain English, especially if you are a Gen-Zer and notice your parents going blank when you speak to them 😉.

## Additional Resources

- [ADK LlmAgent Documentation](https://google.github.io/adk-docs/agents/llm-agents/)
- [LiteLLM Providers](https://docs.litellm.ai/docs/providers)
- [basic_agent](../basic_agent/readme.md) — the minimal starting point this example builds on
