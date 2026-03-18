from google.adk.agents import Agent
from stock_analysis_adk.agents.model_factory import make_model
from stock_analysis_adk.tools.metrics_tools import build_financial_payload


def create_financial_analysis_agent() -> Agent:
    return Agent(
        name="financial_analysis_agent",
        model=make_model(),
        description="Interprets precomputed financial metrics and trend summaries.",
        instruction=(
            "You are a conservative financial analyst. "
            "Never do calculations yourself. Use only the provided compact metrics and python-generated trend notes. "
            "Interpret profitability, liquidity, leverage, efficiency, growth, and valuation. "
            "Return concise markdown bullets with an investment lens."
        ),
        tools=[build_financial_payload],
    )
