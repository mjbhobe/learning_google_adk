# Build Agents with the ADK

## Agent, tools, and runners: The ADK model
In this section we'll discover what the Google Agent Development Kit (ADK) is, what are its core components, how they fit together, and how to configure and run a simple agent.

### What is the ADK and where it fits

The ADK is Google's open source framework for building, debugging, evaluating and deploying AI agents at enterprise scale. It provides a structured, production-grade layer over the model APIs (such as the OpenAI API or Google Gen AI API or Anthropic API). This allows you to focus on designing the agent's behavior, rather than wiring up boilerplate.

ADK supports Python, TypeScript, Go, Java and Kotlin. Feature availability varies across language implementations, and _Python is the most complete implementation_. The **ADK is model-agnostic**, meaning that you can 'point it' at Gemini, Claude, OpenAI, Ollama, or _any provider supported by  LiteLLM_ (an opensource library, which provides a unified interface to dozens of model providers). You can swap models without rewriting your agent logic.

The key distinction from call model API directly is orchestration. When you call a model API directly, you handle context assembly, tool dispatch, retry logic, and state management yourself. The _ADK handles all that infrastructure_, so your code expresses what an agent does, not how the runtime manages it.

Select the ADK of your task required one or more of the following:

| Feature | Description |
| :-- | :-- |
| **Managed Tool**<br/>(or, Specialized Agent Tooling) | Your agent relies on external functions, requiring automatic schema generation from Python signatures, access to shared session state via **ToolContext**, or integration with MCP and OpenAI servers. |
| **Multi-step Workflows**<br/>(or, Multi-step Reasoning) | The system executes a sequence of decisions or transformations that don't fit in a single prompt. |
| **Multi-agent Collaboration**<br/>(or, Orchestration & Collaboration) | Specialized agents work together on a large problem |
| **Production Operations**<br/>(or, Production Reliability) | The system handles observability, evaluation, and deployment at scale. |

To illistrate the technical requirements, consider a production-grade customer support system configured to manage billing anamolies, order tracking, and returns. This domain exemplifies the core operational challenges of the framework through several key patterns:

| Feature | Description |
| :-- | :-- |
| **Managed Tool**<br/>(or, Specialized Agent Tooling) | Dedicated macro agents utilize specialized tools and APIs to query and mutation-test backend systems. |
| **Multi-step Workflows**<br/>(or, Multi-step Reasoning) | Incoming customer requests are complex and require sequential, multi-layered reasoning steps to resolve. |
| **Multi-agent Collaboration**<br/>(or, Orchestration & Collaboration) | Multiple specialist agents operate autonomously under the governance of a centralized coordinator agent. |
| **Production Operations**<br/>(or, Production Reliability) | The entire architecture is engineered to execute deterministically, reliabily, and at scale within a production environment.|

### Components of the ADK

The ADK organizes everything around four core components: **Agents, Models, Tools, and the Runner**. 

* **Agents**: Agents are autonomous units of work that receive a task, decide which actions to take, optionally use tools, and return a result. ADK's primary agent type is `google.adk.agents.Agent` (also called `LlmAgent`), which uses a language model (such as Gemini, Claude etc.) as its reasoning agent.

  The ADK also provides **workflow agents** types that orchestrate other agents _without using a model_ making the orchestration decision. **SequentialAgent** runs sub-agents one after another, **ParallelAgent** runs them concurrently, and **LoopAgent** repeats a sub-agent until some condition is met.

* **Models**: Models are the language models that power agent reasoning. You specify a model but its identifier string (e.g. `model="gemini-2.5-flash"`), and the ADK handles the API calls, token management, and response parsing. You could use a different model per-agent, so different agents in the same system can use different models based on capability and cost.

* **Tools:** Tools extend what an agent can do. A tool is any Python function you pass to an agents **tools** list (e.g., `tools=[get_weather, get_time]`). ADK will use the function's name, docstring, and parameter types to build the tool schema. The model reads that schema to know when and how to call the tool.

  The ADK also supports advanced integrations, like OpenAPI and Model Context Protocol (MCP) tools.

* **Runner:** The runner ties it all together. When you call `adk run` or `adk web`, the ADK instantiates a _local_ runner. This runner manages the event loop, routes user messages to the correct agent, dispatches tool calls, and streams results back. When you are ready for Production, this exact same runner sits behind the API server you deploy to Cloud Run or the Google Kubernetes Engine (GKE).

The following diagram shows you how these 4 components interact with each other - the agent sits at the center and draws on the model (LLM) for reasoning.

<div align="center">
<img src="images/adk_components.png" alt="Components of the ADK"/>
</div>

### Configuring a simple agent

An **Agent** in the ADK requires 3 things to work: 
* A **name**
* A **model**
* and an **instruction**

Everything else is optional, but shapes how the agent behaves in a multi-agent system.

Here is an example of a minimalistic agent:

```python
from google.adk.agents import Agent

# dummy function representing a tool
def lookup_account(account_id: str):
  """retrieves the current balance and status of a given billing account.

  Args:
    account_id: The unique identifier for customer account.
  Returns:
    dict: The account details, or an error status if not found
  """

  # NOTE: the doc-string of a tool function is very important
  # be as descriptive as possible about what the function does, describe ALL parameters (args) and return value.
  # These details will help agent figure out which tool to call, with what params and for what purpose

  return query_billing_database(account_id)

billing_agent = Agent(
  name="billing_agent",
  model="gemini-flash-latest",
  instruction="""
    You are a billing specialist. Answer the questions 
    about account balances, payments histories and invoices.
  """,
  tools=[lookup_account],
)

```

In this example, `lookup_account` is a Python function that queries a billing database to fetch billing details given an account ID.

Parameters of the `Agent` constructor:

* The **name** must be a _unique string identifier_. In a multi-agent system, the name is how a co-ordinator agent refers to this specialist agent when delegating tasks. So choose names that describe the agents role. This name must confirm to Python variable naming conventions.
* The **model** is the model identifier string. The ADK resolves this to the correct API endpoint. We have used `"gemini-flash-latest"`, which is a technique of future-proofing model aliases. Model strings are intrinsically version-specific (for example, `gemini-2.5-flash`), but using the `latest` alias ensures that the system automatically resolves that to the current recommended Flash model. For example, as of June 2026, `"gemini-flash-latest"` will automatically resolve to `"gemini-3.1-flash"`.
* The **instruction** is the most important parameter. **It's the system prompt that defines the agent's persona, its scope, its constraints, and any guidance for tool use**. A well written instruction keeps the agent on task and prevents it from attempting things outside its responsibility/remit. Keep the instruction very specific - an agent that knows exactly what it handles, and what it doesn't, behaves more reliably.
* The **tools** list contains functions the agent can call. The ADK wraps each function automatically, using its docstring and type hints as the tool schema - hence it's important to define very clear & detailed doc strings and type hints for parameters (and return types, where possible). The model will read that schema to decide when and how a tool should be invoked.

These **additional 3 parameters** are worth knowing, especially if you are going to develop multi-agent systems:

* The **description** is a _concise summary of what the agent does_. In a multi-agent system, a co-ordinator (agent) reads this description to decide which specialist (sub-agent) to route a task to. **If you plan to use this agent as a sub-agent, write the description as a single sentence that clearly states the agents scope**. For example `"A billing agent to query account balances, payment histories and invoices"`.
* The **output_key** is an optional string. When set, the ADK writes this agent's final response into a session state under that key, making it available to downstream agents in a workflow. For example, setting `output_key="billing_response"` lets a downstream aggregator agent read the billing result without the co-ordinator needing to pass it explicitly.
* The **output_schema** is an optional string. When you are _forcing_ the agent to produce output in a structured format (for example as a JSON object or Pydantic `BaseModel` derived class), you should use `output_schema` instead of `output_key`. However, `output_schema` is incompatible with tools on some models, so check the model-specific documentation before combining them in a single agent. This is a known problem with Anthropic Claude models (Claude 3, 3.5, and 4.6 Sonnet) and Gemini Flash 1.5 Flash and earlier models for example.

Here is the agent definition with all these new parameters:

```python
from google.adk.agents import Agent

billing_agent = Agent(
  name="billing_agent",
  model="gemini-flash-latest",
  description="A billing agent to query account balances, payment histories and invoices",
  instructions="""....""",
  tools=[lookup_account, list_invoices, payment_history_lookup],
  output_key="billing_response",
)
```

### Agent Runtime vs Agent Sandbox

The ADK ships with a CLI that handles the full development loop: scaffold, run, inspect, iterate.

You start a new project with `adk create my_agent` (replace `my_agent` with your project name). This creates a sub-directory called `my_agent` in the current directory; and within the `my_agent` subdirectory, it creates 3 files `agent.py` (for your agent definition), `__init__.py`, and a `.env` file for your API key.

Open `agent.py` and define your agent as `root_agent`. ADK's runner discovers your agent by looking for a module-level variable named (exactly) `root_agent`; using any other name means the runner won't fint it and will error on startup. For mult-agent setup, you can define multiple agents in this `agent.py` file, but the main or orchestration agent must be defined with the `root_agent` variable (excatly).

To interact with (run) the agent in a terminal session, use `adk run my_agent` on the prompt. This opens a REPL where you type messages to the agent and see its responses inline, including which tools are called and what they returned.

For a richer development experence, `adk web` launches a browser interface at `http://localhost:8000`. It gives you a _chat panel_ and a _trace view_ inside the window. The latter will show you each step of the agent's reasoning: which model calls were made, which tools were invoked, what each tool returned, and (most importantly) how the agent arrived at its final response. It's the fastest way to validate that your instructions and tools are providing the behavoir expected.

When you are ready to expose the agent as a REST API endpoint, the `adk api_server adk_agent` command starts an HTTP server that accepts user messages and streams agent responses, using the same runner that powers the terminal and browser mode.

**The development loop is:** write the agent -> run `adk web` (or `adk run`) -> send test message(s), read the trace -> adjust the instruction or tools or both -> repeat. Most agent behavior issues (such as incorrect tool selection, off-topic responses, missing context etc.) are visible in the trace view within the first few test messages.

### Advantages of the ADK

The ADK offers several key advantages for developers building agentic applications:

* **Multi-agent systems:** Build modular, scalable applications by composing specialized agents into hierarchical structures.
* **Rich tool ecosystem:** Equip agents with pre-built tools, custom functions, or integrations from frameworks like LangChain and CrewAI.
* **Flexible Orchestration:** Define predictable pipelines with workflow agents or use LLMs for adaptive, dynamic routing.
* **Integrated Developer Experience:** Develop and debug locally with a powerful CLI and an interactive UI to inspect execution step-by-step.
* **Built-in Evaluation:** Systematically assess performance by evaluating response quality and execution trajectories against test cases.
* **Deployment Ready:** Easily containerize and scale agents on Agent Runtime, Cloud Run, or custom Docker infrastructure.

While other SDKs allow you to query models, ADK provides a higher-level framework that handles the complex coordination between multiple models for you.

## ADK tools, context, and state

In this section we'll discuss how the ADK converts Python functions into tools the model can use. We'll discover how these tools reach into sessions state and influence agent flow. We'll also learn to observe and control the agent execution lifecycle using callbacks and plugins.

### Building Tools the model can use
When you pass a Python function to an agent's **tools** list, the ADK inspects its signature to build a JSON schema. The model receives that schema alongside the agent's instructios and uses it to know what tools are available, when to call each tool, and what arguments to pass to the respective tool. Refining the scheme correctly ensures reliable tool usage.

Three elements define schema quality:

1. **The function name**: The function name becomes the tool name. Use specific, descriptive function names. For example, `lookup_account` tells the model exactly what the function does; `get_data` is does not.
2. **The docstring**: The docstring is your most important element. It's the model's only guide to when and why yo call your tool. Describe the tool's purpose, what each parameter expects, and how to interpret the return value, including error cases as clearly and as detailed as possible. If the tool returns `{"status":"error"}` when an account does not exist, say so explicitly. **A vague/incomplete docstring produces unreliable tool selection; a precise one keeps the model on task**.
3. **Type hints**: Use type hints on all parameters and return type to sharpen the schema the model uses to construct arguments. Omitting them produces weaker schema and less consistent invocations.

The following example demonstrates how a specific function name, a detailed docstring, and proper type hinting come together to for a high-quality tool schema:

```python
def get_account_balance(account_id: str) -> dict:
  """returns the current balance for a given account.
  
  Args:
    account_id: the unique identifier for the customer account.
  Returns:
    dict: 'balance' (float) on success, or "error" (str) if not found
  """
```

If your function accepts a **ToolContext** parameter (covered later), don't document it in the docstring. ADK injects it automatically and it isn't part of the schems the model sees!

The agents `instructions="""..."""` must also encode inter-tool dependencies. **The model has no implicit awareness of tool sequencing**. It only knows what the docstring says. **If one tool's output must feed another's input, state that dependency explicitly in the instructions**. For example: `"Use lookup_account first; if account is active, call fetch_transactions with the returned account ID"`.

The ADK also supports MCP tools and OpenAPI tools. MCP tools connect and agent to any server implementing the Model Context Protocol and exposes its capabilities as callable tools. OpenAPI tools generate one tool for each endpoint in an OpenAPI specification. Both integrate through the same `tools=[...]` list.

### ToolContext: State, flow and artifacts

When a tool needs to do more than just compute and return a value, add a **ToolContext** parameter to its signature. The ADK injects the object automatically at invocation time. Because it's injected, it's invisible to the model and not part of the schema, so don't include it in the docstring.

**ToolContext** provides a tool with four capabilities:
1. **State Access**: `tool_context.state` is a read-write view of the session state. A tool can read data set earlier in the conversation and write values that downstream agents will pick up. Because that state is written by your application (and not by the LLM), it's trustworthy for authorization checks and policy flags the model shouldn't be able to forge.

```python
def fetch_account(account_id: str, tool_context: ToolContext) -> dict:
  """Returns account data for authorized user."""
  
  # session_user_id is set by the app at session start, not supplied
  # by the LLM
  authorized_id = tool_context.state.get("session_user_id")
  if account_id != authorized_id:
    return {"error": "Access denied!"}
  return lookup_account(account_id)
```

2. **Flow Control**: 

    * `tool_context.actions` lets a tool signal what should happen next
    * Setting `tool_context.actions.transfer_to_agent="agent_name"` hands the conversation to another agent ("agent_name")
    * Setting `tool_context.actions.escalate=True` passes control up to the parent agent in a multi-agent hierarchy.
    * Setting `tool_context.actions.skip_summarization=True` tells the ADK to pass the tool's raw output directly to the model without summarizing it first.
    * Use this to ensure that the model reasons over the full, high-fidelity result.
  
3. **Artifacts**: for large data (documents, images, query result sets), use `tool_context.load_artifact(name)` and `tool_context.save_artifact(name, data)`.

    **Artifacts are named binary objects stored in the session**. Keeping large data in artifacts rather than return value or in state prevents the event payload from bloating the context window (thus saving you on token costs!).
  
4. **Authentication**: for tools that call authenticated external APIs, `tool_context.request_credentials(auth_config)` initiates an authentication flow, and `tool_context.get_get_auth_response()` retrieves the credentials once provided.

### Session state and multi-agent coordination

The **session state is a shared scratchpad that persists across the entire conversation**. It's a key-value store with string keys and serializable values (strings, numbers, booleans, dicts, lists). Every agent, tool, and callback in a session can read and write it through the ADK.

**State prefixes control scope**

Four prefixes determine where the value lives and how long it lasts:

* **Session-scoped (no prefix)**: visible to all agents in this conversation, but not others.
* **User-scoped (user)**: persists across all sessions for a given user; use this for user preferences and profile data.
* **App-scoped (app)**: Shared across all users of the application; for global config (e.g. database connection info) or shared templates.
* **Invocation-scoped (temp)**: shared across all agents and tools in the same invocation, but cleared when the invocation ends. Use it for intermediate data you don't need persisted.

**Reading state in agent instructions**

The ADK substitutes `{key}` references in an agent's `instruction=...` string with matching value from session state _before sending the instruction to the model_. 

This is a clean way to personalize and agent's behavior from context set earlier in the conversation. Use `{key?}` for keys that may not exist!

```python
support_agent = Agent(
  name="support_agent",
  model="gemini-flash-latest",
  instruction="""
    You're helping {user:name}. Their preferred language is {user:language}.
  """,
)
```

**Writing state safely**

The ADK tracks state changes as a part of event history. This is what makes persistence work across `InMemorySessionService`, `DatabaseSessionService`, and `VertexAiSessionService`. Two patterns are safe for writing:

* `output_key` on an agent writes the agent's final text response to state automatically. It's the simplest coordination pattern for passing an agent's result to a downstream step.
* Direct assignment through `tool_context.state` in a tool, or `callback_context.state` in a callback. The ADK captures these changes in the event's state delta.

**Never write directly to `session.state` outside these managed contexts**! Doing so bypasses event tracking, breaks persistence with database-backed session services, and isn't thread-safe when agents run in parallel.

**State as a co-ordination mechanism**

When a `SequentialAgent` or `ParallelAgent` runs sub-agents, they all share the same invocation and therefore the same `temp: state`. Non-temp state is visible across the entire session. The `output_key` pattern is how specialist agents hand off results to the next step without a coordinator passing data explicitly. An upstream agent writes its results under a known key, and downstream agent reads it from its `instruction` template or from a tool.

In a multi-agent pipeline, the state scheme is an implicit contract between every agent that reads or writes it. A key renamed in one agent silently breaks every other agent that depends on it. Define key names, prefixes, and value shapes in a shared constant module and import it everywhere.

### Callbacks and Plugins

Callbacks and plugins let you observe and intercept agent behavior at predefined execution points without modifying the agent or tool code itself.

Callbacks are functions you register on an agent at creation time. The ADK calls them at six different lifecycle checkpoints, organized as three before/after pairs: Around agent run, around each model call, and around each tool call.

Each callback receives a **context object** with the current session state and agent metadata. Return `None` to let execution proceed normally; return a value to short-circuit the next step and use your return as its result.

```python
def block_restricted(callback_context: CallbackContext, llm_request: LlmRequest):
  last = llm_request.contents[-1].parts[0].text if llm_request.contents else ""
  
  if "RESTRICTED" in last.upper():
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text="That request cannot be processed!")]))
  
  # else 
  return None  # proceed normally!

  agent = Agent(
    name="guarded_agent",
    model="gemini-flash-latest",
    instruction="...",
    before_model_callback=block_restricted,
  )
```

Each callback pair has a natural use case:

* `before_model_callback` and `after_model_callback` are the right place for input guardrails, prompt modifications, and response filtering.
* `before_tool_callback` and `after_tool_callback` handle argument validation and output post processing.
* `before_agent_callback` and `after_agent_callback` handle access control and response enrichment at the agent boundary.

Plugins also receive hooks that agent callbacks don't: on every incoming user message, at run start, and when a model or tool call raises an error. The error hooks let you intercept a failure and return a synthetic response, or return `None` to re-raise and let the retry system handle it.

The following diagram illustrates the sequential flow through one agent execution turn, showing six callback checkpoints as blue intercept nodes. Plugin calls (orange) appear before each corresponding agent callback. The dashed arrows show short-circuit paths that skip the next step when callback returns a non-None value.


