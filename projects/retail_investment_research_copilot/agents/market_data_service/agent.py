from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from logger import get_logger

from .tools import render_market_snapshot

load_dotenv(override=True)

MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")

logger = get_logger("retail_investment_copilot:market_data_service")


def build_root_agent():
    logger.info("In market_data_service::build_root_agent()")

    intake_agent = LlmAgent(
        name="ticker_intake",
        model=MODEL,
        instruction=(
            "You receive a user prompt containing a stock ticker. "
            "Extract the ticker symbol, normalize it if needed, and restate the request in one concise line."
        ),
        output_key="normalized_request",
    )

    snapshot_agent = LlmAgent(
        name="fundamental_and_technical_analyst",
        model=MODEL,
        tools=[render_market_snapshot],
        instruction=(
            "Use the render_market_snapshot tool to fetch market data for the ticker in: {normalized_request}\n"
            "Produce a compact markdown section covering key fundamentals (PE, PB, ROE, D/E, dividend yield, "
            "revenue/earnings growth) and technical context (price vs SMA50/SMA200, 52-week change, "
            "daily volatility). Be factual. Note any missing or unreliable data explicitly."
        ),
        output_key="market_snapshot_summary",
    )

    interpretation_agent = LlmAgent(
        name="signal_interpreter",
        model=MODEL,
        instruction=(
            "Use the market snapshot below to write a plain-language interpretation.\n\n"
            "{market_snapshot_summary}\n\n"
            "Cover: valuation posture (cheap/fair/expensive), price trend (bullish/bearish/sideways), "
            "volatility level, and balance-sheet quality. Maximum 200 words."
        ),
        output_key="market_interpretation",
    )

    # parallel_research = ParallelAgent(
    #     name="parallel_market_research",
    #     sub_agents=[snapshot_agent, interpretation_agent],
    # )

    final_agent = LlmAgent(
        name="market_data_packager",
        model=MODEL,
        instruction=(
            "Combine the inputs below into one concise markdown note for the downstream memo service.\n\n"
            "## Request\n{normalized_request}\n\n"
            "## Market Snapshot\n{market_snapshot_summary}\n\n"
            "## Signal Interpretation\n{market_interpretation}\n\n"
            "Preserve all numbers. Do not add commentary beyond what is already present."
        ),
        output_key="final_market_data_note",
    )

    return SequentialAgent(
        name="market_data_pipeline",
        # sub_agents=[intake_agent, parallel_research, final_agent],
        sub_agents=[intake_agent, snapshot_agent, interpretation_agent, final_agent],
    )
