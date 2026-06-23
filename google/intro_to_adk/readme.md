# Introduction to the Google Agent Development Kit (ADK)
(Source [Google Partner Skill Development Course](https://partner.skills.google/course_templates/1275))

<div align="left">
<img src="images/adk_logo.png" width="250" height="200" alt="Tools with MCP"/>
</div>

<!-- Google color palette
<font color="#4285F4">Blue</font> 
<font color="#EA4335">Red</font> 
<font color="#FBBC05">Yellow</font> 
<font color="#34A853">Green</font> 
<font color="#E37400">Orange</font>
<font color="#202124">Dark Gray</font>
<font color="#F1F3F4">Light Gray</font>
-->

## Introducing the Agent Development Kit (ADK)

AI Agents are poised for explosive growth in the coming years: By 2028, over 33% of enterprise software will incorporate
AI agents. AI agents will automate 15% of daily work decisions. This shift towards autonomous operations will
significantly transform businesses across all industries.

<div align="center">
<img src="images/rise_of_ai_agents.png" width="450" height="200" alt="Tools with MCP"/>
</div>


**AI Agents are interactive partners that help answer complex questions and complete tasks.** There are some key areas
where AI agents are already having a big impact.

<div align="center">
<img src="images/areas_of_ai_agent_impact.png" width="450" height="150" alt="Tools with MCP"/>
</div>

* AI agents enable data scientists to get insights faster by automating data-related tasks like creating datasets,
  spotting anomalies in data, and generating visualizations.
* They assist employee productivity by helping train and onboard, complete daily tasks such as underwriting, verifying
  claims, and processing returns.
* AI agents help research analysts quickly answer questions using proprietary data, such as summarizing research,
  recalling past events, and pointing human researchers towards useful lines of thinking.
* And they can help developers complete software development tasks, including designing systems, writing code, logging
  bugs, creating tickets, and debugging.

With Google Cloud, developers can build agents at their preferred level of abstraction.

### Ways to build Agents

There are a **range of methods for agent building** that range from highly customizable and flexible, which require more
effort

<div align="center">
<img src="images/levels_of_dev_abstractions.png" width="450" height="300" alt="Tools with MCP"/>
</div>

* You can **build a bespoke custom agent framework**, completely built to your own specific needs, **using Vertex
  components** like function calling and Gemini.
* You can **build custom agents with** a low level orchestration framework, like **LangChain/LangGraph or GenKit**.
* Or you **can build an agent-specific framework, using the Google ADK**, for balance of deterministic control and
  convenience, providing more support, to allow you nearly as much freedom as lower-level tools, while making it much
  easier to build and evaluate complex multi-agent systems.
* Or you could use other agentic frameworks, such as Smolagent, Crew AI, AG2 or Autogen.
* Finally, you have the **out-of-the box solutions, such as Agentspace and Conversational Agents**, which are very easy
  to use, but offer much less flexibility.

### Paths to build Agents on the GCP

Google Cloud provides four key paths for building an agent.

<div align="center">
<img src="images/4_paths_to_building_agents.png" width="450" height="100" alt="Tools with MCP"/>
</div>

| GCP Path                                                  | Details                                                                                                                                                |
|:----------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Customer Engagement Suite, with Conversational Agents** | Use when you want external-facing conversational agents that can integrate with human support teams and existing telephony and communication platforms |
| **Agentspace** | Use when you want internal search to accelerate knowledge exchange throughout your organization, across your drives, chat, mail, ticketing platforms, databases, and more, including AI assistant support |
| **Open source frameworks or from scratch with Agent Engine** | Use when you want to  build something custom, you can use basic building blocks and start building from the ground up, for example, with the Google Gen AI SDK or LangChain, where you will also need to make decisions about infrastructure and hosting.|
| **ADK with Agent Engine** | Use when you want the freedom of custom development with support for communication between agents through conversation history and shared state. |

The **Agent Development Kit (ADK)** makes it easier to build multi-agent systems, while handling challenges of agent communication for you. It also frees you from infrastructure decisions through deployment to Agent Engine, a fully managed runtime, so you can focus on building logic and interactions between agents while resources are allocated and autoscaled for you.


### Who is the ADK designed for?

* Designed for developers, who can create agents within their applications, with a code-centric approach, and no AI expertise required.
* Designed to empower developers to build, manage, evaluate and deploy AI-powered agents.
* The ADK is a client-side Python SDK, enabling developers to quickly build and customize multi-agent systems.
* ADK’s multi-agent systems allow a parent agent to steer the flow to various sub agents to complete different, specialized tasks as required.

<div align="center">
<img src="images/multi_agent_systems.png" width="450" height="150" alt="Multi-agent systems"/>
</div>

## Introducing the Agent Development Kit (ADK)

<div align="center">
<img src="images/adk_advantages.png" width="900" height="200" alt="ADK Advantages"/>
</div>

The ADK offers several key advantages for developers building agentic applications: What makes this special is it’s much easier for multi-agent collaboration.

* With **multi-agent systems** you can easily build applications composed of multiple, specialized agents arranged hierarchically.
* There are **several pre-built, custom and community tools** that give agents abilities beyond conversation, letting them interact with external APIs, search information, run code, or call other services. With the ADK's open system, we can easily integrate tools from other popular agent frameworks (like LangChain, and CrewAI), leveraging existing investments and community contributions.
* ADK also **makes evaluation easier**.
* It **provides** a convenient, user-friendly local development user interface, with **tools to help debug your agents and multi-agent systems**.
* The ADK **provides callbacks** that can be used to invoke functions during various stages of a flow.
* **Provides session memory for stateful conversations**, which enables agents to recall information about a user across multiple sessions, providing long-term context (in addition to short-term session State).
* It **integrates artifact storage** to facilitate agent collaboration on documents.
* And, it **can be deployed to Agent Engine, for fully-managed agent infrastructure**.

## Developing Agents with the ADK

The Google ADK is built around a few key primitives and concepts that make it powerful and flexible:

<div align="center">
<img src="images/adk_key_concepts.png" width="450" height="150" alt="ADK Key Concepts"/>
</div>


* **The Agent is the fundamental worker unit designed for specific tasks**.  Agents can **use language models for complex reasoning, or to act as controllers to manage workflows**. Agents **can coordinate complex tasks, delegate sub-tasks using LLM-driven transfer, or explicit Agent Tool invocation**, enabling modular and scalable solutions. With **native streaming support, you can build real-time, interactive experiences** with native support for bi-directional streaming, with text and audio. **Integrates seamlessly with underlying capabilities like the Gemini Live API**, often enabled with simple configuration changes. **Artifact Management allows agents to save, load, and manage versioned artifacts, files or binary data**, like images, documents, or generated reports, associated with a session or user, during their execution.
* Google ADK **provides a rich tool ecosystem, which equips agents with diverse capabilities**. It supports integrating custom functions, using other agents as tools, leveraging built-in functionalities like code execution, and interacting with external data sources and APIs. Support for long-running tools allows handling asynchronous operations effectively. There is also integrated developer tooling, so that you can develop and iterate locally with ease. ADK includes tools like a command-line interface (CLI) [`adk run`] and a Web UI [`adk web`] for running agents, inspecting execution steps, debugging interactions, and visualizing agent definitions. **Session Management for session and state handles the context of a single conversation** (the Session), including its history (as Events) and the agent’s working memory for that conversation (the State). An Event is the basic unit of communication representing things that happen during a session (such as user message, agent reply, and tool use), forming the conversation history. And **Memory enables agents to recall information about a user across multiple sessions**, providing long-term context, this is distinct from short-term session State.
* ADK **provides flexible orchestration that enables you to define complex agent workflows using built-in workflow agents alongside LLM-driven dynamic routing**. This allows for both predictable pipelines and adaptive agent behavior. As part of this orchestration Google ADK **uses a Runner**, which is the engine that manages the execution flow, orchestrates agent interactions based on Events, and coordinates with backend services. The ADK **has built-in Agent evaluation**, which means you can assess agent performance systematically. The **framework includes tools to create multi-turn evaluation datasets, and run evaluations locally**, through the CLI or UI, to measure quality and guide improvements. And **Code Execution provides the ability for agents (usually using Tools) to generate and execute code**, to perform complex calculations or actions.
* **Callbacks** are custom code snippets you provide to run at specific points in the agent's process, **allowing for checks, logging, or behavior modifications**. Google **ADK deploys to Agent Engine, a fully managed Google Cloud service** enabling developers to deploy, manage, and scale AI agents in production. Agent Engine handles the infrastructure to scale agents in production, so you can focus on creating intelligent and impactful applications. **Planning**, is an advanced **capability where agents can break down complex goals into smaller steps and plan how to achieve them** like a ReACT planner.
* As part of the interactive developer tooling, Google **ADK provides you tools to help debug your agents, interactions and multi-agent systems**. Your application traces will be collected by Cloud Trace, a tracing system that collects latency data from your distributed applications and displays it in the Google Cloud console. **Cloud Trace can capture traces from applications deployed on Agent Engine**, and it can help you debug the different calls performed between your LLM agent and its tools, before returning a response to the user. Finally, **models are the underlying Large Language Models**, like Gemini, or Claude, that power ADKs LLM Agents, enabling their reasoning, and language understanding abilities. Though optimized for Gemini models, the ADK framework can work with all popular LLMs, including open-sourced LLMs.

### Components of an Agent

An agent can execute the steps of a certain workflow to accomplish a goal, and can access any required external systems and tools to do so. There are **4 main components of an agent**:

<div align="center">
<img src="images/components_of_agents.png" width="450" height="250" alt="Components of Agents"/>
</div>

* The <font color="#34A853">**models**</font> are used to reason over goals, determine the plan and generate a response. An ADK agent can use multiple models.
* <font color="#4285F4">**Tools**</font> are used to fetch data, perform actions or transactions by calling other APIs or services.
* <font color="#FBBC05">**Orchestration**</font> is the mechanism for configuring the steps required to complete a task, and the logic for processing over these steps, and accessing the required tools. It _maintains memory and state, including the approach used to plan, and any data provided or fetched, as well as the necessary tools_.
* And the <font color="#EA4335">**runtime**</font> is used to execute the system when invoked after receiving a query from an end user.

### Configuring the ADK

In this section, we'll discuss how to configure a local Python environment to develop agents with the ADK, and different ways to run your agents.

Let's assume that we'll be developing all our ADK projects in sub-folders of the `~/adk_projects` folder on a Mac or Linux machine (or `c:\adk_projects` on Windows). Also, we'll assume that you are managing your local Python environments using `uv`, and it is installed on your machine. For `uv` installation instructions [follow this link](https://docs.astral.sh/uv/getting-started/installation/).

#### Create a Virtual environment
* Open your terminal and navigate to the `~/adk_projects` (or `c:\adk_projects`) folder.
* Run the following command to create the virtual environment **and activate it** - it is important that you activate your local environment before installing any packages.

```bash
# creates a local Python environment with Python >= 3.10
# replace 3.10 in command below with your preferred version
$ ~/adk_projects> uv init --python 3.10
Initialized project `adk-projects`

# above command will create 3 files in ~/adk_projects
# main.py, readme.md and pyproject.toml

# now initialize the virtual env in a .venv sub-folder (IMP)
$ ~/adk_projects> uv venv .venv
Using CPython 3.12.11
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate

# activate your local environment
$ ~/adk_projects> source .venv/bin/activate  # on Mac/Linux
OR
$ c:\adk_projects> source .venv/Scripts/activate  # on Windows

# you should see a changed prompt like the one below
(.venv)
$ ~/adk_projects>
```
* Install the `google_adk` package in your newly created & activated Python environment as follows

```bash
(.venv)
$ ~adk_projects> uv add google_adk
# will install several packages....
```

* To test that `google_adk` is available in the local environment, type `adk --version` on the command line. If it shows the adk version (may take some time), then you are all set!

```bash
(.venv)
$ ~adk_projects> adk --version
adk, version 2.3.0
```

#### ADK project directory structure

* Each ADK project **MUST BE** created in it's own sub-directory. Suppose our new project is to be created in the `welcome_agent` sub-folder off `~/adk_projects` parent folder, here is the directory structure (and recommended file naming conventions)

```
~/adk_projects/
├── .venv/                      # Your local virtual environment (we just created using uv commands)
├── pyproject.toml              # Managed by uv (your dependencies - uv add ... commands will update this file)
│
└── welcome_agent/              # Your main agent module directory
    ├── __init__.py             # Exposes the agent and configurations
    ├── .env                    # Hidden file that contains your LLM API key & other globals
    ├── agent.py                # Defines the main Agent object and its instructions
    ├── tools.py                # (Optional) contains Python functions the agent can use as tools
    ├── workflows.py            # (Optional) Maps out multi-agent graph flows
    └── main.py                 # local test script runner / application entry point
```

#### Creating your first agent

1. Create the `welcome_agent` folder. Within the folde create `.env`, `agent.py`, and `__init__.py` files (see folder structure above)
2. Open `agent.py` in your favourite IDE or editor and type in the following code

```python
from dotenv load_dotenv

from google.adk.agents import Agent

root_agent = Agent(
  name="welcome_agent",
  model="gemini-3.1-flash-lite',
  description="Greeter agent",
  instruction="""
    You are a friendly assistant that greets the user and responds to their queries
  """,
)
```

**NOTE:**

* The _main_ agent must be assigned to the `root_agent` variable. In this example we have just one agent. But real applications usually have multiple agents working together - one of them is the _main_ driver (or _orchestrator_ agent).
* The _name_ parameter (**mandatory**) is a user-friendly name you give the agent. Though this is a string, the **contents of this string must _strictly_ match Python variable naming conventions**! So `welcome_agent` is ok, but `Welcome Agent` is **not ok**.
* The _model_ parameter (**mandatory**) is the name of a Google Gemini model hosted on AI Studio (or Vertex AI). _Strictly speaking_ this is not correct - it could be any LLM model supported by ADK, which are all the popular models (from OpenAI, Anthropic, and open source models like the LLamas, Mistrals etc.), but the way we declare those is slightly different. _For the first few lessons_ assume this is a Gemini model only. Use any valid Gemini model name (such as `gemini-2.5-flash`, `gemini-3.1-flash-lite` etc.)
* The _description_ parameter (**optional**) describes the role of the Agent. If you have used system prompts that tell the LLM what role it should impersonate, for example, "You are an experienced Financial Advisor at a leading Bank", this is what the description parameter does. It is optional for single agent application, like this one, but _is required for multi-agent_ applications. It helps the _main_ agent identify what each of the other agents does (what role it plays) and helps the _main_ agent transfer the workflow to the correct sub-agent. I would treat this as a mandatory parameter for all practical purposes.
* The _instruction_ parameter (**mandatory**) - this is the most important parameter. This represents the instructions you give the agent to act - what is it that you want the agent to accomplish.
* Other parameters, which we will cover in later lessons are _tools_ [which is a list of tools that the agent can use], parameters that define input & output schemas and call back functions.

3. Open `__init__.py` and type in the following code:

```python
from . import agent
```

* Add your API key to the `.env` file. You should get your API key from Google AI Studio website. Your `.env` file should look something like this:

```bash
GOOGLE_PROJECT_ID=<<Your Google Project Name on Google Cloud Console>>
GOOGLE_API_KEY=<<Your API Key>>
```

#### Running your agent

<div align="center">
<img src="images/running_agents.png" width="450" height="80" alt="Components of Agents"/>
</div>

Google ADK offers four primary ways to interact with your agents: Through **Web UI** (`adk web`), Or a **Command-Line Interface (CLI)** (`adk run`), An **API Server** (`adk api_server`), or the **Programmatic Interface** (i.e. Python code). 

The way you define your agent (the core logic within agent dot py) is the same regardless of how you choose to interact with it. The difference lies in how you initiate and manage the interaction.

1. With Web UI (`adk web`), you can interact with your agent through a user-friendly web browser. It is a good option for visual interaction while developing your agent and monitoring agent behavior. **It should only be used for local testing, it is not suitable for a production environment**.

To get started with Web UI, open your terminal, and run the following commands (shown for a Linux/Mac session):

```bash
# cd to **PARENT** folder of your agent's project folder \
# (i.e. parent of folder where you saved the agent.py file!)
$> cd ~/adk_projects  
# activate local Python environment (changes prompt)
$ ~/adk_projects> source .venv/bin/activate
# type adk web <folder_name of agent's project folder>
(.venv)
$ ~/adk_projects> adk web welcome_agent
# this will open up a web-UI from which you can select & 
# run your agent.
```

2. With the CLI (`adk run`) you use terminal commands to interact directly with your agent. The CLI is a good option for quick tasks, scripting, automation, and developers comfortable with terminal commands. **This should also only be used for local testing, it is not suitable for a production environment**.

To get started with CLI, open your terminal, and run the following commands (shown for a Linux/Mac session) - these the same as for the web interface EXCEPT for the last command. Instead of `adk web` you use `adk run`.

```bash
# cd to **PARENT** folder of your agent's project folder \
# (i.e. parent of folder where you saved the agent.py file!)
$> cd ~/adk_projects  
# activate local Python environment (changes prompt)
$ ~/adk_projects> source .venv/bin/activate
# type adk web <folder_name of agent's project folder>
(.venv)
$ ~/adk_projects> adk run welcome_agent
# will kick off the agent and allow you to interact with it
# from command line
```

3.  Run your agent as a **REST API** , allowing other applications to communicate with it. Running an API server is a **good option for integration with other applications, building services that use the agent, and remote access to the agent**. This approach **can be used for production environments** 😀.

To use the API interface, open your terminal, and run the following commands (shown for a Linux/Mac session). Again, these steps are the SAME as the `adk web` or `adk run` options, but for the last step, where we use `adk api_server` instead.

```bash
# cd to **PARENT** folder of your agent's project folder \
# (i.e. parent of folder where you saved the agent.py file!)
$> cd ~/adk_projects  
# activate local Python environment (changes prompt)
$ ~/adk_projects> source .venv/bin/activate
# type adk web <folder_name of agent's project folder>
(.venv)
$ ~/adk_projects> adk api_server welcome_agent
# this will start a local API server, using Flask, on port 8000
```

After the server starts, you can then interact with your agent through REST API calls.

4. Finally, the **Programmatic Interface** allows you to integrate ADK directly into your Python applications, or interactive notebooks (like Jupyter and Colab). Unlike the CLI, Web UI, and API server, you don't need the specific project structure, as previously described. Instead you’ll be using a `Session` and `Runner`. You can define and interact with your agent within the same file or notebook cell.

The programmatic interface provides deep integration within applications, custom workflows, notebooks, and fine-grained control over agent execution. **This approach can be used for production environments**. We will cover this later in the lessions, where we'll code all the steps in a Python function (or functions)

**NOTE:** 

1. You can use either `adk_run` (the command line version) or `adk_web` (the 'visual' tool/utility) to run test your _simple_ agents. 
2. The argument to this is the name of the folder holding your `agent.py` file. 
3. You can define multiple agents in the `agent.py` file, but _only one_ must be marked as the _root agent_ with the `root_agent = ...` variable. The `adk_web`/`adk_run` commands look for this variable and run it as the main agent (especially where you have multi-agent apps)

Here's how your session could look like (NOTE: I have created projects under a different parent folder. Other than that, everything else above holds):


