# Agent Development Kit (ADK) Crash Course

This repository contains examples for learning Google's Agent Development Kit (ADK), a powerful framework for building LLM-powered agents.

## Getting Started

### Setup Environment

You only need to create one virtual environment for all examples in this course. Follow these steps to set it up - I'll be using `uv` to manage my local Python environment. You can install `uv` for your operating system by following [these installation instructions](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Create virtual environment in the root directory
uv init --python 3.14

# Activate (each new terminal)
# macOS/Linux:
source .venv/bin/activate
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Install dependencies
uv add -r requirements.txt
```

Once set up, this single environment will work for all examples in the repository.

### Setting Up API Keys
Depending on which LLM you prefer, follow the instructions below. I have used Open AI in all examples

**Google Gemini API Key**

* Go to Google AI Studio and sign in with your Google account.
* Click on the "Get API key" or "API keys" option.
* Click the "Create API key" button.
* Choose to create the key in a new project or select an existing Google Cloud project. A new project is simpler.
* Copy and securely store the generated key. You can view it again in the console, but it is best to save it safely to avoid loss. 
* In your local `.env` file, set the value of `GOOGLE_API_KEY=<<key you just created>>`. 
* Also add another line `GOOGLE_GENAI_USE_VERTEXAI=FALSE` to the `.env` file.

**OpenAI API Key**
* Go to the OpenAI Platform and log in or sign up for an account.
* Click on the "API keys" section.
* Click the "Create new secret key" button and give your key a name.
* Copy and securely store the full secret key string, which displays only once.
* In your local `.env` file, set the value of `OPENAI_API_KEY=<<key you just created>>`. 
* **NOTE:** We cannot use Google supplied tools, such as `google_search` with Open AI models!

**Anthropic Claude API Key**
* Go to the Anthropic Console and sign in or create an account.
* Click the key icon (API Keys).
* Click the "Create Key" button and provide a name.
* Copy and securely store the full API key, which displays only once.
* In your local `.env` file, set the value of `ANTHROPIC_API_KEY=<<key you just created>>`. 
* **NOTE:** We cannot use Google supplied tools, such as `google_search` with Anthropic AI models!


Each example folder contains a `.env.example` file. For each project you want to run:

1. Navigate to the example folder
2. Rename `.env.example` to `.env` 
3. Open the `.env` file and replace the respective placeholder with your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   OR
   OPEN_AI_API_KEY=your_api_key_here
   OR
   ANTHROPIC_API_KEY=your_api_key_here
   ```
(you can always set all 3 keys!)

You'll need to repeat this for each example project you want to run.

## Examples Overview

Here's what you can learn from each example folder:

### 1. Basic Agent
Introduction to the simplest form of ADK agents. Learn how to create a basic agent that can respond to user queries. This agent does not use external tools, so all responses come from pre-trained data only - agent will not be able to respond to any "recent event" questions.

See [readme.md](01-basic-agent/readme.md)

### 2. Tool Agent
Learn how to enhance agents with tools that allow them to perform actions beyond just generating text. For example, enabling web searching allows agent to fetch the most recent events informations.
**NOTE:** You _CANNOT_ use Google provided _internal_ tools, such as `google_search` with non-Google LLMs.

See the readme.md file on the workaround we have used, since we are using OpenAI in all examples.

### 4. Structured Outputs
Learn how to use Pydantic models with `output_schema` to ensure consistent, structured responses from your agents.

### 5. Sessions and State
Understand how to maintain state and memory across multiple interactions using sessions.

### 6. Persistent Storage
Learn techniques for storing agent data persistently across sessions and application restarts.

### 7. Multi-Agent
See how to orchestrate multiple specialized agents working together to solve complex tasks.

### 8. Stateful Multi-Agent
Build agents that maintain and update state throughout complex multi-turn conversations.

### 9. Callbacks
Implement event callbacks to monitor and respond to agent behaviors in real-time.

### 10. Sequential Agent
Create pipeline workflows where agents operate in a defined sequence to process information.

### 11. Parallel Agent
Leverage concurrent operations with parallel agents for improved efficiency and performance.

### 12. Loop Agent
Build sophisticated agents that can iteratively refine their outputs through feedback loops.

## Official Documentation

For more detailed information, check out the official ADK documentation:
- https://google.github.io/adk-docs/get-started/quickstart

## NOTE
This code is built on-top of the code shared by Brandon Hancock as part of his [ADK Masterclass Video on YouTube](https://www.youtube.com/watch?v=P4VFL9nIaIA&list=PLbM_IDvvYBgkSu2SRoX0JFBJA7ucpKuuI) - here is [Brandon's code repo](https://github.com/bhancockio/agent-development-kit-crash-course/tree/main)