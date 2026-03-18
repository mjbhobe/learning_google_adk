from google.adk.agents import Agent
from stock_analysis_adk.agents.model_factory import make_model
from stock_analysis_adk.tools.news_tools import build_sentiment_payload


def create_sentiment_analysis_agent() -> Agent:
    return Agent(
        name="sentiment_analysis_agent",
        model=make_model(),
        description="Interprets precomputed public-news sentiment signals.",
        instruction=(
            "You are a market sentiment analyst. "
            "Do not fetch or score headlines yourself. Use only the provided sentiment payload. "
            "Interpret the balance of positive, neutral, and negative signals and the likely near-term implications."
        ),
        tools=[build_sentiment_payload],
    )
