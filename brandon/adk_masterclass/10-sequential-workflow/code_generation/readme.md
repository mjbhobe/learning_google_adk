# Sequential Agents in ADK

This example demonstrates how to implement a Sequential Agent in the Google Agent Development Kit (ADK). Here we will show an example of how a team of 3 agents can generate Python code per your requirements. For example, the user enters a prompt like:

> Write my Python code that converts Celsius temperature to Fahrenheit

And the agent team generates the code for you.

The main agent in this example, `code_pipeline_agent`, is a Sequential Agent that executes sub-agents in a predefined order, with each agent's output feeding into the next agent in the sequence.

## What are Sequential Agents?

Sequential Agents are workflow agents in ADK that:

1. **Execute in a Fixed Order**: Sub-agents run one after another in the exact sequence they are specified
2. **Pass Data Between Agents**: Using state management to pass information from one sub-agent to the next
3. **Create Processing Pipelines**: Perfect for scenarios where each step depends on the previous step's output

Use Sequential Agents when you need a deterministic, step-by-step workflow where the execution order matters.

## Code Generation Pipeline Example

In this example, we've created `code_pipeline_agent` as a Sequential Agent that implements a code generation pipeline. This Sequential Agent orchestrates three specialized sub-agents:

1. **Code Writer Agent**: Generates Python code based on the user's requirements
   - Writes clean, PEP 8-compliant code with Google-style docstrings
   - Outputs a complete Python code block
2. **Code Reviewer Agent**: Reviews the generated code and provides feedback
   - Evaluates correctness, readability, efficiency, edge cases, and best practices
   - Outputs a concise, bulleted list of review comments (or "No major issues found.")
3. **Code Refactorer Agent**: Applies the review feedback to improve the code
   - Refactors the original code based on the reviewer's comments
   - If no issues were found, returns the original code unchanged
   - Outputs the final, polished Python code block

### How It Works

The `code_pipeline_agent` Sequential Agent orchestrates this process by:

1. Running the Code Writer first to generate code from the user's specification
2. Running the Code Reviewer next (which accesses the generated code via state)
3. Running the Code Refactorer last (which accesses both the generated code and review comments)

The output of each sub-agent is stored in the session state using the `output_key` parameter:

- `generated_code`
- `review_comments`
- `refactored_code`

## Project Structure

```
10-sequential-workflow/
│
├── code_generation/                    # This example folder
│   ├── code_pipeline_agent/            # Main Sequential Agent package
│   │   ├── __init__.py                 # Package initialization
│   │   ├── agent.py                    # Sequential Agent definition (root_agent)
│   │   │
│   │   └── subagents/                  # Sub-agents folder
│   │       ├── code_writer_agent/      # Code generation agent
│   │       │   ├── __init__.py
│   │       │   └── agent.py
│   │       │
│   │       ├── code_reviewer_agent/    # Code review agent
│   │       │   ├── __init__.py
│   │       │   └── agent.py
│   │       │
│   │       └── code_refactorer_agent/  # Code refactoring agent
│   │           ├── __init__.py
│   │           └── agent.py
│   │
│   ├── .env.example                    # Environment variables example
│   ├── main.py                         # CLI driver program (run with uv run main.py)
│   ├── sample_requirements.md          # Sample prompts to test the pipeline
│   └── readme.md                       # This documentation
```

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

2. Copy the `.env.example` file to `.env` and add your API key (depending on the LLM you prefer):

```
GOOGLE_API_KEY=your_api_key_here
# or
OPENAI_API_KEY=your_api_key_here
# or
ANTHROPIC_API_KEY=your_api_key_here
```

### Running the Example 

The same commands will work in a Linux/Mac shell or a Windows Powershell or CMD shell.

(**NOTE:** `$>` denotes command prompt -- don't type this!)

```bash
$> cd 10-sequential-workflow/code_generation
$> adk web code_pipeline_agent
OR
$> adk run code_pipeline_agent
```

If using `adk web`, select "code_pipeline_agent" from the dropdown menu in the web UI.

Alternatively, you can run the example using the CLI interface with uv:

```bash
$> cd 10-sequential-workflow/code_generation
$> uv run main.py
```

The CLI interface prompts you interactively for code generation requirements. Type `exit` at the prompt to quit.

## Example Interactions

Try these example interactions from `sample_requirements.md`:

### Simple Problem Example:

```
Write a Python module that converts between Celsius, Fahrenheit, and Kelvin.
Include functions for all 6 conversion directions and a CLI that accepts a value and unit.
```

### Medium Complexity Example:

```
Implement a password strength checker that scores a password (0–100) based on length, character variety, common patterns, and dictionary words. Return a score plus actionable feedback messages.
```

### Complex Problem Example:

```
Implement an LRU (Least Recently Used) cache in Python that also supports TTL (time-to-live) expiry per key. It should be thread-safe and have O(1) get/put operations.
```

## How Sequential Agents Compare to Other Workflow Agents

ADK offers different types of workflow agents for different needs:

- **Sequential Agents**: For strict, ordered execution (like this example)
- **Loop Agents**: For repeated execution of sub-agents based on conditions
- **Parallel Agents**: For concurrent execution of independent sub-agents

## Additional Resources

- [ADK Sequential Agents Documentation](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
