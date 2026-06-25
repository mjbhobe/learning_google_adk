# Craft Agents with Persistent Memories

LLMs are inherently stateless, meaning their awareness is confined to the limited "context window" of a single API call. This makes building intelligent AI agents difficult. They require continuous access to operating instructions, factual data, and immediate conversational context to function effectively.

**So what's the solution?**

**Stateful and personal AI - starting with _context engineering_**. To create stateful agents that remember, learn, and personalize interactions, developers must build this context for every single conversational turn. This process - context engineering - evolves beyond static prompt engineering by dynamically assembling a state-aware prompt using data, conversation history, and external knowledge. Context engineering plays a critical role in creating powerful, personalized, and persistent AI experience. 

There are two major components that make this happen:

1. **Sessions**: The immediate container for an entire conversation, holding chronological history of the dialog and the agent's turn-by-turn working memory.
2. **Memory**:  The mechanism of long-term persistence, which captures and consolidates key information across multiple sessions to provude a continuous and personalized experience for the user.

## Context Engineering

LLMs are inherently stateless. Outside of their training data, their reasoning and awareness are confined to the information provided within the "context window" of a single API call. This presents a fundamental problem: AI agents must be equipped with operating instructions, factual data, and immediate conversational information to understand their current task.

To build intelligent agents that can remember, learn and personalize interactions, you must construct this context for every single turn of the conversation. This dynamic assembly and management of information is known as context engineering.

### Prompt Engineering vs Context Engineering

Context Engineering represents a necessary evolution from traditional prompt engineering. To understand the difference, consider how they handle information:

| **Prompt Engineering** | **Context Engineering** |
| :-- | :-- |
| Focuses on crafting optimal, often static, system instructions | Addresses the entire payload, dynamically constructing a state-aware prompt based on the user, conversation history and external data |


Ultimately Context Engineering involves strategically selecting, summarizing, and injecting different types of information to maximize relevance while minimizing noise. Because external systems - such as RAG databases, session stores, and memory managers - hold much of this context, your agent framework must constantly orchestrate these systems to retrieve and assemble the final prompt.

The goal of context engineering is to ensure that the model has no more an dno less than the most relevant information to complete the task.

### Analyze the anatomy of Context

To achieve this "perfect recipe" it's helpful to understand what ingredients go into the context window. Context Engineering governs the assembly of complex payload that can include a variety of components, which can be broken down into three categories:

1. **Context Guide Reasoning**: This category defines the agent's fundamental reasoning patterns and available actions, dictating its behavior:
    
    * **System Instructions**: High-level directives defining the agent's persona, capabilities, and constraints.
    * **Tool definitions**: Schemas for APIs or functions the agent can use to interact with the outside world.
    * **Few-shot examples**: Curated examples that guide the model's reasoning process via in-context learning.

2. **Evidential and factual data**: This is the substantive data the agent reasons over, including pre-existing knowledge and dynamically retrieved information for the specific task; it serves as the 'evidence' for the agent's response.

    * **Long-term memory**: Persisted knowledge about the user or topic, gathered across multiple sessions.
    * **External knowledge**: information retrieved from databases or documents, often using RAG.
    * **Tool outputs**: The data or result returned by a tool.
    * **Sub-agent outputs**: The conclusions or results returned by specialized agents that have been delegated a specific sub-task.
    * **Artifacts**: Non-textual data (e.g., files, images) associated with the user or session.

3. **Working Context**: This final category grounds the agent in the current interaction, defining the immediate task:

    * **Conversation history**: The turn-by-turn record of the current interaction.
    * **State or scratchpad**: Temporary, in-progress information or calculations the agent uses for its immediate reasoning process.
    * **User's prompt**: The immediate question to be addressed.

### Why not include everything inside the context window?

One of the biggest challenges in building a context-aware agent is dealing with an every-growing conversation history. Although modern models _can_ handle massive transcripts, sending the entire history everytime creates two significant drawbacks:

| | |
|:--|:--|
| 1. **Increased cost and latency**: Processing a massive context window takes more time and costs more money. | 2. **"Context Rot"**: As the prompt gets longer, the model's ability to pay attention to the most critical information diminishes.|