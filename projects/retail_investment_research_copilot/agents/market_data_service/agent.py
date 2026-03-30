from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
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
            "Use the render_market_snapshot tool to fetch a free market snapshot. "
            "Then produce a compact markdown section with key fundamentals and technical context. "
            "Be factual and mention obvious data quality gaps."
        ),
        output_key="market_snapshot_summary",
    )

    interpretation_agent = LlmAgent(
        name="signal_interpreter",
        model=MODEL,
        instruction=(
            "Interpret the market snapshot already available in state. "
            "Discuss valuation, trend posture, volatility, and balance-sheet quality in simple language."
        ),
        output_key="market_interpretation",
    )

    parallel_research = ParallelAgent(
        name="parallel_market_research",
        sub_agents=[snapshot_agent, interpretation_agent],
    )

    final_agent = LlmAgent(
        name="market_data_packager",
        model=MODEL,
        instruction=(
            "Create a market-data summary for the downstream memo service. "
            "Combine normalized request, market snapshot summary, and market interpretation into one markdown note."
        ),
        output_key="final_market_data_note",
    )

    return SequentialAgent(
        name="market_data_pipeline",
        sub_agents=[intake_agent, parallel_research, final_agent],
    )
