from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from logger import get_logger

load_dotenv(override=True)

logger = get_logger("retail_investment_copilot:memo_service:agent")

MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")


def build_root_agent():
    logger.info("In memo_service::build_root_agent() ->")

    intake_agent = LlmAgent(
        name="memo_intake",
        model=MODEL,
        instruction=(
            "Read the JSON payload. Extract ticker, horizon, risk appetite, market data note, and news note. "
            "Create a clean internal brief for specialist agents."
        ),
        output_key="research_brief",
    )

    valuation_agent = LlmAgent(
        name="valuation_specialist",
        model=MODEL,
        instruction=(
            "Using the research brief, explain whether the stock looks obviously cheap, fair, or expensive. "
            "Do not fabricate ratios beyond what is present."
        ),
        output_key="valuation_view",
    )

    momentum_agent = LlmAgent(
        name="momentum_specialist",
        model=MODEL,
        instruction=(
            "Using the research brief, explain what the price trend and volatility imply for the selected horizon."
        ),
        output_key="momentum_view",
    )

    risk_agent = LlmAgent(
        name="risk_specialist",
        model=MODEL,
        instruction=(
            "Using the research brief, identify the most important downside risks and uncertainties."
        ),
        output_key="risk_view",
    )

    parallel_stage = ParallelAgent(
        name="parallel_specialist_stage",
        sub_agents=[valuation_agent, momentum_agent, risk_agent],
    )

    writer_agent = LlmAgent(
        name="memo_writer",
        model=MODEL,
        instruction=(
            "Write a business-friendly markdown investment memo with these sections: "
            "Company snapshot, Bull case, Bear case, What the market data says, What the news says, "
            "Decision stance, and What would change my mind. "
            "End with one of: Watchlist / Hold / Accumulate / Avoid. "
            "This is educational, not investment advice."
        ),
        output_key="draft_memo",
    )

    critic_agent = LlmAgent(
        name="memo_critic",
        model=MODEL,
        instruction=(
            "Critique the draft memo in state. Check clarity, internal consistency, unsupported claims, "
            "and whether the recommendation matches the evidence. Produce actionable rewrite guidance."
        ),
        output_key="memo_critique",
    )

    rewriter_agent = LlmAgent(
        name="memo_rewriter",
        model=MODEL,
        instruction=(
            "Rewrite the memo using the critique in state. Improve structure, reduce overclaiming, "
            "and tighten the final recommendation."
        ),
        output_key="draft_memo",
    )

    refinement_loop = LoopAgent(
        name="memo_refinement_loop",
        sub_agents=[critic_agent, rewriter_agent],
        max_iterations=2,
    )

    finalizer = LlmAgent(
        name="finalizer",
        model=MODEL,
        instruction=(
            "Return the final markdown memo from state. Preserve headings and make it readable."
        ),
        output_key="final_memo",
    )

    return SequentialAgent(
        name="memo_pipeline",
        sub_agents=[
            intake_agent,
            parallel_stage,
            writer_agent,
            refinement_loop,
            finalizer,
        ],
    )
