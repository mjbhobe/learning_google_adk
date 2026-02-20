"""
07-loop-agent.py

Not all problems have a straightforward, one-shot solution. Sometimes, we need to
propose a solution, critique it, and refine it until it meets a specific constraint.

For this, the ADK offers the LoopAgent. This workflow agent repeatedly executes a
sequence of sub-agents until a specific condition is met. This is perfect for building
"perfectionist" agents that can plan, critique, and improve their own work.

In this example, we'll develop a "Perfectionist Planner", which involved 3 agents:
a. The "Planner" agent, which creates the initial plan based on user's input, which
   includes any constraints, such as budget, interests (no museums!), cusine (no pork) etc.
b. A "Critic" agent that checks the plan against a constraint(s) specified (such as travel
   between destinations should not be > 30 mins)
c. A "Refiner" agent - should the "Critic" agent find problems with the "Planner" agent's
   output, this agent takes the feedback and creates a new, improved plan. If the critic is
   happy, it calls a special exit_loop tool to stop the process.

We have an overaching "LoopAgent" manages this "critique & refine" cycle, ensuring we don't
get stuck in an infinite loop by setting a max_iterations limit.
Finally a "SequentialAgent" sequences the "Planner" -> "LoopAgent" ("Critic" -> "Refiner"
sub-agents).
"""

import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools import google_search
from google.adk.tools import ToolContext

from utils import load_agent_config, run_agent_query, web_search
from logger import get_logger

# load API keys
load_dotenv(override=True)
# console = Console()
# this line exists ONLY to address wierd bug with git bash
# shell on Windows, where rich.Prompt(...) call with color
# coding folds up the display
console = Console(force_terminal=True, legacy_windows=False)

logger = get_logger("loop_agent")

COMPLETION_PHRASE = "The plan is feasible and meets all constraints."

# load our agents config
planner_agent_config = load_agent_config("planner_agent")
critic_agent_config = load_agent_config("critic_agent")
refiner_agent_config = load_agent_config("refiner_agent")
iterative_planner_config = load_agent_config("iterative_planner_agent")

# define our agents ----------------------------------------

# agent that makes the initial travel plan
planner_agent = LlmAgent(
    name="planner_agent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=planner_agent_config["description"],
    instruction=planner_agent_config["instruction"],
    tools=[web_search],
    output_key="current_plan",
)

# agent that critiques the plan made by planner based on
# user's constraints.
critic_agent = LlmAgent(
    name="critic_agent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=critic_agent_config["description"],
    instruction=critic_agent_config["instruction"],
    tools=[web_search],
    output_key="criticism",
)


def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the plan is approved, signaling the loop should end."""
    logger.info(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    # save the approved plan before it gets overwritten
    tool_context.state["approved_plan"] = tool_context.state.get("current_plan", "")
    tool_context.actions.escalate = True
    return {}


refiner_agent = LlmAgent(
    name="refiner_agent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=refiner_agent_config["description"],
    instruction=refiner_agent_config["instruction"],
    tools=[web_search, exit_loop],
    output_key="current_plan",
)

# ----- Refinement loop - the LoopAgent that executes critique + refine loop ------
refinement_loop = LoopAgent(
    name="refinement_loop", sub_agents=[critic_agent, refiner_agent], max_iterations=3
)

# ----- Sequential agent that sequences planner + (critic & refine loop) ------
iterative_planner_agent = SequentialAgent(
    name="iterative_planner_agent",
    sub_agents=[planner_agent, refinement_loop],
    description=iterative_planner_config["description"],
)


async def main():
    session_service = InMemorySessionService()
    app_name = "loop_agent_app"
    my_user_id = "adk_adventurer_001"
    # NOTE: we'll need a common session across all queries
    my_session: Session = await session_service.create_session(
        app_name=app_name, user_id=my_user_id
    )
    # add this message to session, so Agent finds it
    my_session.state["COMPLETION_PHRASE"] = COMPLETION_PHRASE

    query = ""
    while True:
        query = Prompt.ask(
            "[bright_yellow]Query (or type 'exit' or press Enter to quit): [/bright_yellow]",
            default="exit",
        )
        # query = input()
        if query.strip().lower() == "exit":
            console.print("[bright_yellow]Goodbye![/bright_yellow]")
            break

        # console.print(f"[green]🗣️ User Query:[/green] '{query}'")

        final_response = await run_agent_query(
            iterative_planner_agent,
            query,
            session_service,
            session=my_session,
            user_id=my_user_id,
        )

        # fetch the final plan genrated
        # NOTE: the final_response above will be the last response from
        # refiner_agent and not the final plan. The plan is saved in session
        updated_session = await session_service.get_session(
            app_name=app_name, user_id=my_user_id, session_id=my_session.id
        )
        final_plan = updated_session.state.get(
            "approved_plan", "**FATAL:** Could not fetch the plan!"
        )

        console.print("[green]\n" + "-" * 50 + "\n[/green]")
        console.print("[green] Travel Plan:[/green]")
        console.print(Markdown(final_plan))
        console.print("[green]\n" + "-" * 50 + "\n[/green]")


if __name__ == "__main__":
    asyncio.run(main())
