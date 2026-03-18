from google.adk.agents import Agent
from stock_analysis_adk.agents.model_factory import make_model


def create_recommendation_agent() -> Agent:
    return Agent(
        name="recommendation_agent",
        model=make_model(),
        description="Synthesizes all sub-agent outputs into a final recommendation.",
        instruction=(
            "You are the final investment recommendation agent. "
            "Use only the supplied section analyses and compact raw metric highlights. "
            "Do not invent facts. "
            "Return markdown with: Recommendation, Why, Key Risks, and What would change your view."
        ),
        tools=[],
    )
