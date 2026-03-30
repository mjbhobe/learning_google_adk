from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from logger import get_logger

from .tools import fetch_rss_news

logger = get_logger("retail_investment_copilot:news_service:agent")

load_dotenv(override=True)

MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")


def build_root_agent():
    logger.info("In news_service::build_root_agent() ->")
    fetch_agent = LlmAgent(
        name="news_fetcher",
        model=MODEL,
        tools=[fetch_rss_news],
        instruction=(
            "Use the fetch_rss_news tool with the stock ticker found in the user prompt. "
            "Return a concise news digest and do not invent headlines."
        ),
        output_key="raw_news_digest",
    )

    sentiment_agent = LlmAgent(
        name="news_sentiment_analyst",
        model=MODEL,
        instruction=(
            "Analyze the raw news digest in state. "
            "Identify 3 to 5 positives, negatives, and uncertain items affecting the company."
        ),
        output_key="news_sentiment",
    )

    risk_agent = LlmAgent(
        name="news_risk_analyst",
        model=MODEL,
        instruction=(
            "Review the raw news digest in state and infer potential business, regulatory, or execution risks. "
            "Stay conservative when evidence is weak."
        ),
        output_key="news_risks",
    )

    parallel_agents = ParallelAgent(
        name="parallel_news_review",
        sub_agents=[sentiment_agent, risk_agent],
    )

    synthesis_agent = LlmAgent(
        name="news_synthesis",
        model=MODEL,
        instruction=(
            "Combine the raw news digest, sentiment view, and risk view into a concise markdown note "
            "for a downstream investment memo."
        ),
        output_key="final_news_note",
    )

    return SequentialAgent(
        name="news_pipeline",
        sub_agents=[fetch_agent, parallel_agents, synthesis_agent],
    )
