"""
Memo service agent pipeline.

Performance notes
-----------------
* All prompts use explicit {state_key} interpolation so ADK injects the
  exact value rather than the model having to search the full state dict.
* LoopAgent max_iterations reduced from 2 → 1  (saves 2 LLM round-trips).
* The redundant `finalizer` LlmAgent has been removed; the rewriter's
  output is the final memo.  The runtime returns the last event text, so
  draft_memo is returned directly.
"""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from logger import get_logger

load_dotenv(override=True)

logger = get_logger("retail_investment_copilot:memo_service:agent")

MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")


def build_root_agent():
    logger.info("In memo_service::build_root_agent() ->")

    # ------------------------------------------------------------------
    # Stage 1 — Intake
    # Parses the raw JSON payload and produces a clean prose brief that
    # all downstream agents can read without having to re-parse JSON.
    # ------------------------------------------------------------------
    intake_agent = LlmAgent(
        name="memo_intake",
        model=MODEL,
        instruction=(
            "You will receive a JSON payload containing the following fields: "
            "ticker, horizon, risk_appetite, market_data_analysis (or market_data), and news_analysis. "
            "Extract all fields and write a concise internal research brief in plain prose. "
            "Label each section clearly: Ticker, Horizon, Risk Appetite, Market Data Summary, News Summary. "
            "Do not add opinions — just organise the facts."
        ),
        output_key="research_brief",
    )

    # ------------------------------------------------------------------
    # Stage 2 — Parallel specialist analysis
    # Each agent receives the research_brief directly via {research_brief}
    # interpolation, so ADK injects the exact text with no ambiguity.
    # ------------------------------------------------------------------
    valuation_agent = LlmAgent(
        name="valuation_specialist",
        model=MODEL,
        instruction=(
            "You are a valuation analyst. Use the research brief below.\n\n"
            "{research_brief}\n\n"
            "In 150 words or fewer, state whether the stock looks cheap, fair, or expensive. "
            "Cite only ratios already present in the brief. Do not fabricate numbers."
        ),
        output_key="valuation_view",
    )

    momentum_agent = LlmAgent(
        name="momentum_specialist",
        model=MODEL,
        instruction=(
            "You are a technical/momentum analyst. Use the research brief below.\n\n"
            "{research_brief}\n\n"
            "In 150 words or fewer, explain what the price trend and volatility data imply "
            "for the investment horizon stated in the brief."
        ),
        output_key="momentum_view",
    )

    risk_agent = LlmAgent(
        name="risk_specialist",
        model=MODEL,
        instruction=(
            "You are a risk analyst. Use the research brief below.\n\n"
            "{research_brief}\n\n"
            "In 150 words or fewer, identify the three most important downside risks. "
            "Stay conservative — do not speculate beyond what the brief contains."
        ),
        output_key="risk_view",
    )

    parallel_stage = ParallelAgent(
        name="parallel_specialist_stage",
        sub_agents=[valuation_agent, momentum_agent, risk_agent],
    )

    # ------------------------------------------------------------------
    # Stage 3 — First-draft memo
    # Writer receives all four keys directly, removing any need for the
    # model to search through full session state.
    # ------------------------------------------------------------------
    writer_agent = LlmAgent(
        name="memo_writer",
        model=MODEL,
        instruction=(
            "You are a senior investment analyst writing an educational memo. "
            "Use the inputs below — do not invent data not present in them.\n\n"
            "## Research Brief\n{research_brief}\n\n"
            "## Valuation View\n{valuation_view}\n\n"
            "## Momentum View\n{momentum_view}\n\n"
            "## Risk View\n{risk_view}\n\n"
            "Write a concise markdown investment memo with these sections:\n"
            "1. Company Snapshot\n"
            "2. Bull Case\n"
            "3. Bear Case\n"
            "4. What the Market Data Says\n"
            "5. What the News Says\n"
            "6. Decision Stance (end with exactly one of: Watchlist / Hold / Accumulate / Avoid)\n"
            "7. What Would Change My Mind\n\n"
            "Keep each section to 3–5 sentences. "
            "Add a footer: *This memo is for educational purposes only and is not investment advice.*"
        ),
        output_key="draft_memo",
    )

    # ------------------------------------------------------------------
    # Stage 4 — Single refinement pass (critic → rewriter)
    # max_iterations=1 means one critic call + one rewriter call (2 LLM
    # round-trips) vs the previous 2 iterations (4 round-trips).
    # The rewriter's output IS the final memo — no separate finalizer needed.
    # ------------------------------------------------------------------
    critic_agent = LlmAgent(
        name="memo_critic",
        model=MODEL,
        instruction=(
            "Review the draft memo below.\n\n"
            "{draft_memo}\n\n"
            "Check for: unsupported claims, internal inconsistencies, unclear language, "
            "and whether the Decision Stance matches the evidence. "
            "Produce a numbered list of specific, actionable rewrite instructions. "
            "Be concise — maximum 5 items."
        ),
        output_key="memo_critique",
    )

    rewriter_agent = LlmAgent(
        name="memo_rewriter",
        model=MODEL,
        instruction=(
            "Rewrite the memo below using the critique as a guide.\n\n"
            "## Draft Memo\n{draft_memo}\n\n"
            "## Critique\n{memo_critique}\n\n"
            "Apply every critique point. Keep the same section structure. "
            "Do not add new data not present in the draft. "
            "Return only the final markdown memo — no preamble."
        ),
        output_key="draft_memo",   # overwrites in-place; becomes the final output
    )

    refinement_loop = LoopAgent(
        name="memo_refinement_loop",
        sub_agents=[critic_agent, rewriter_agent],
        max_iterations=1,          # was 2 — saves 2 full LLM round-trips
    )

    return SequentialAgent(
        name="memo_pipeline",
        sub_agents=[
            intake_agent,       # 1 LLM call
            parallel_stage,     # 3 LLM calls (concurrent)
            writer_agent,       # 1 LLM call
            refinement_loop,    # 2 LLM calls (critic + rewriter)
            # Total: 7 LLM calls, 3 of which run in parallel
            # (was 9 calls with max_iterations=2 + finalizer)
        ],
    )
