# Build Enterprise Agents with Code Execution on Gemini Enterprise Agent Platform

Source : [Google Partner Training](https://partner.skills.google/paths/4144/course_templates/1745/documents/633755)

In this document, we'll explore the Code execution feature of the Gemini Enterprise Agent Platform (formerly known as the _Vertex AI Platform_), which lets AI agents safely generate and run Python code in isolated sandbox environments. We'll see how the Agent Sandbox fits into the broader platform architecture, how to configure and operate Code Execution sandboxes using the Agent Platform SDK, and how to integrate code execution into agent workflows with the ADK.

## Gemini Enterprise Agent Platform and the Agent Sandbox

In this section we'll learn what the Gemini Enterprise Agent Platform is and where Code Execution fits inside it. Many agent tasks, such as complex mathematical calculations or data analysis, require an agent to generate and run untrusted code. Giving an agent the ability to run arbitraty code raises an immediate question: **Where does that code actually run**? We'll explore platform architecture and see how Agent Sandbox is designed to answer that question safely.

### The Gemini Enterprise Agent Platform

The **Gemini Enterprise Agent Platform** (formerly known as the Vertex AI Platform), is Google Cloud's platform for building, scaling, governing, and optimizing AI Agents. It launched in April 2026 as the evolution of the Vertex AI Agent Builder. It consolidates model selection, agent development, and enterprise operations into one integrated platform.

The platform organized its capabilities into four areas:

| Area | Description | 
| :-- | :-- |
| **Build** | **Tools for creating agents**: **Agent Studio** for low-code development, the **Agent Development Kit (ADK)** for code-first engineering, **sub-agents** for multi-agent workflows, **Agent Garden templates**, and batch and event-driven agent support. |
| **Scale** | **Infrastructure for running agents in production**: **Agent Runtime** for deployment, **Agent Memory Bank** for long-term context, **Agent Sessions** for tracking conversations, and **Agent Sandbox** for safe execution of risky operations. |
| **Govern** | **Controls for secure, compliant agent deployments**: **Agent Identity**, **Agent Registry**, **Agent Gateway**, **Agent Anamoly Detection**, **Agent Threat Detection**, and **Agent Security Dashboard** |
| **Optimize** | **Tools for improving agents over time**: Agent Simulation, Agent Evaluation, Agent Observability, and Agent Optimizer. |

All the Vertex AI services and roadmap evolutions are now delivered through Agent Platform. If you've worked with Vertex AI Agent Builder before, you'll recognize the building blocks; the platform adds the Scale & Govern layers that enterprise production deployments require.

The following diagram maps these four areas and highlights where Agent Sandbox sits within Scale:

<div align="center">
<img src="images/gemini_enterprise_ai_platform.png" alt="Gemini Enterprise AI Platform"/>
</div>

For an enterprise application, these capabilities work together:

* The Build tools help engineers author a portfolio-analysis agent, Scale runs it reliabily and safely.
* Govern ensures it meets the compliance requirements, and Optimize continuously improves it.

## The Scale area: Agent Runtime and Agent Sandbox

Within the Scale capability area, two components handle the execution side of agents: **Agent Runtime** and **Agent Sandbox**

They serve different purposes and operate in different trust domains.

**Agent Runtime**

Agent Runtime is a trusted, long-running environment where your agent's core logic executes. It deliveres sub-second cold starts and supports long running agents. This is where agent reasons, decides what actions to take, and co-ordinates with tools. Agent Memory bank handles long term context retention, while Agent Sessions tracks conversation state. Both are distinct Scale components that work alongside Agent Runtime.

An Agent Engine is the top-level container resource that owns your sandboxes. You create one before provisioning a sandbox, and it persists across the sandbox lifecycle.

<<TODO: continue from here: >>
