<link rel="stylesheet" href="./tabs.css">

# Craft ADK Agents with Persistent Memories

Large Language Models (LLMs) are inherently stateless, meaning their awareness is confined to the limited "context window" of a single API call. This makes building intelligent AI agents difficult. They require continuous access to operating instructions, factual data, and immediate conversational context to function effectively.

**So what’s the solution?**

Stateful and personal AI - starting with context engineering. To create stateful agents that remember, learn, and personalize interactions, developers must build this context for every single conversational turn. This process—context engineering—evolves beyond static prompt engineering by dynamically assembling a state-aware prompt using user data, conversation history, and external knowledge.

Throughout this course, you’ll explore the critical role of context engineering to empower you to create powerful, personalized, and persistent AI experiences. You’ll also dive into the two core components that make this possible:

1. **Sessions:** The immediate container for the entire conversation, holding the chronological history of the dialog and the agent's turn-by-turn working memory.
2. **Memory:** The mechanism for long term persistence, which captures and consolidated key information across multiple sessions to provide a continuous and personalized experience for the user.

In this course, you’ll learn how to:

* Explain the critical role of context engineering in building stateful agents.
* Distinguish between sessions and memory and explain how they collaborate to enable personalized and persistent AI experiences.
* Design and implement architectural strategies for managing context, conversation history, and long-term knowledge in production-grade agents.

Building intelligent AI agents requires moving beyond static system instructions. Large Language Models (LLMs) process each interaction independently. To make them truly stateful, you must provide a carefully curated package of history, facts, and immediate conversational context.

In this chapter, you'll explore context engineering—the process of dynamically assembling this information to create a state-aware prompt. You'll examine the continuous lifecycle of context management. You'll also discover how to balance the need for rich Al memory against the practical constraints of API costs, quality, and latency. Finally, you’ll explore the underlying Agent Runtime infrastructure that makes data persistence possible in a production environment.

## Define context engineering

Large Language Models (LLMs) are inherently stateless. Outside of their training data, their reasoning and awareness are confined to the information provided within the "context window" of a single API call. This presents a fundamental problem: AI agents must be equipped with operating instructions, factual data, and immediate conversational information to understand their current task.

To build intelligent agents that can remember, learn, and personalize interactions, you must construct this context for every single turn of a conversation. This dynamic assembly and management of information is known as context engineering.

### Compare prompt and context engineering

Context engineering represents a necessary evolution from traditional prompt engineering. To understand the difference, consider how they handle information:

1. **Prompt Engineering:** Focuses on crafting optimal, often static, system instructions.
2. **Context Engineering:** Addresses the entire payload, dynamically constructing a state-aware prompt based on the user, conversion history, and external data.

**Ultimately, context engineering involves strategically selecting, summarizing, and injecting different types of information to maximize relevance while minimizing noise**. Because external systems—such as RAG databases, session stores, and memory managers—hold much of this context, your agent framework must constantly orchestrate these systems to retrieve and assemble the final prompt.

**The goal of context engineering is to ensure the model has no more and no less than the most relevant information to complete its task**.

### Analyze the anatomy of context

To achieve this "perfect recipe," it's helpful to understand exactly what ingredients go into the context window. context engineering governs the assembly of a complex payload that can include a variety of components, which can be broken down into three categories:

**Context to guide reasoning**

This category defines the agent’s fundamental reasoning patterns and available actions, dictating its behavior: 
* **System instructions:** High-level directives defining the agent's persona, capabilities, and constraints. 
* **Tool definitions:** Schemas for APIs or functions the agent can use to interact with the outside world. 
* **Few-shot examples:** Curated examples that guide the model's reasoning process via in-context learning. 

**Evidential and factual data**

This is the substantive data the agent reasons over, including pre-existing knowledge and dynamically retrieved information for the specific task; it serves as the 'evidence' for the agent's response: 

* **Long-term memory:** Persisted knowledge about the user or topic, gathered across multiple sessions. 
External knowledge: Information retrieved from databases or documents, often using  Retrieval-Augmented Generation (RAG). 
* **Tool outputs:** The data or results returned by a tool. 
Sub-agent outputs: The conclusions or results returned by specialized agents that have been delegated a specific subtask.
* **Artifacts:** Non-textual data (e.g., files, images) associated with the user or session. 

**Working context**

This final category grounds the agent in the current interaction, defining the immediate task: 

* **Conversation history:** The turn-by-turn record of the current interaction. 
* **State or scratchpad:** Temporary, in-progress information or calculations the agent uses  for its immediate reasoning process. 
* **User's prompt:** The immediate query to be addressed. 

### Why not just include everything in the context window?

One of the biggest challenges in building a context-aware agent is dealing with an ever-growing conversation history. Although modern models can handle massive transcripts, sending the entire history every time creates two significant drawbacks:

| | |
| :-- | :-- |
| **1. Increased cost and latency** <br/>Processing a massive context window takes more time and costs more money. |  **2. "Context rot"** <br/>As the prompt gets longer, the model's ability to pay attention to the most critical information diminishes. |

Context engineering directly addresses this by dynamically compressing the history. By using techniques like summarizing older messages, or pruning irrelevant details, you preserve vital information while managing the overall token count.

### Examine the context management lifecycle

To build the right context and keep the conversation history manageable, an agent follows a structured cycle during every single turn of a conversation:

![Context Management Lifecycle](images/context_management_lifecycle.png)

1. **Fetch context:** The agent begins by retrieving context—such as user memories, RAG documents, and recent conversation events. For dynamic context retrieval, the agent will use the user query and other metadata to identify what information to retrieve.
2. **Prepare context:** The agent framework dynamically constructs the full prompt for the LLM call. Although individual API calls may be asynchronous, preparing the context is a  blocking, "hot-path" process. The agent cannot proceed until the context is ready. 
3. **Invoke LLM and tools:** The agent iteratively calls the LLM and any necessary tools until a final response for the user is generated. Tool and model output is appended to the context.
4. **Upload context:** New information gathered during the turn is uploaded to persistent  storage. This is often a "background" process, allowing the agent to complete execution while memory consolidation or other post-processing occurs asynchronously. 

#### Work with persistence in ADK

In this course, you’ll focus on Agent Development Kit (ADK) in Gemini platform, the framework designed to empower developers to quickly build, manage, evaluate and deploy AI-powered agents. At the center of the content management lifecycle in ADK there are three fundamental components:

1. **Session:** manages the turn-by-turn state of a _single_ conversation.
2. **Memory:** provides mechanism for long-term persistence, capturing and consolidating key information across multiple sessions.
3. **Skills:**

Skills superpower an agent with capabilities that can be loaded on demand. These skills can evolve and change, and the agent can develop new skills as it learns. The session serves as the temporary scratchpad for a single conversation, while the agent's memory is the meticulously organized filing cabinet, allowing it to recall key information during future interactions.



Work with persistence in Gemini platform



Gemini platform is a unified platform to build, deploy, govern, and optimize enterprise-grade AI agents and model-based solutions. ADK natively integrates with Gemini platform, but you can build agents without using ADK, and still benefit from Gemini platform solutions. Regarding persistence, Gemini platform includes:

Click each flipcard to reveal content








Divider




Summary



Because LLMs are inherently stateless, they start completely fresh with every API call. To build intelligent, continuous experiences, you can rely on context engineering—dynamically assembling system instructions, factual data, and conversation history into an optimized prompt for every turn to prevent context rot.