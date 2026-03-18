from google.adk.agents import Agent
from stock_analysis_adk.agents.model_factory import make_model
from stock_analysis_adk.tools.business_tools import build_business_fundamentals_payload


def create_business_fundamentals_agent() -> Agent:
    return Agent(
        name="business_fundamentals_agent",
        model=make_model(),
        description="Analyzes business fundamentals using a compact precomputed evidence pack.",
        instruction=(
            "You are a disciplined equity research analyst. "
            "You may use the tool if needed, but when the prompt already contains a compact evidence pack, "
            "do not request more data. Do not recalculate anything. "
            "Analyze only: products/services, customers, revenue drivers, market position, value proposition, "
            "moats, revenue concentration risk, scalability, longevity, and resilience. "
            "Return concise markdown bullets only."
        ),
        tools=[build_business_fundamentals_payload],
    )
