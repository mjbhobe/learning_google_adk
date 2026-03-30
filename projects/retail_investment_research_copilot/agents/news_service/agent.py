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
            "Analyse the news digest below.\n\n"
            "{raw_news_digest}\n\n"
            "Identify 3–5 positives, 3–5 negatives, and up to 3 uncertain/ambiguous items "
            "that could affect the company's outlook. Use bullet points per category."
        ),
        output_key="news_sentiment",
    )

    risk_agent = LlmAgent(
        name="news_risk_analyst",
        model=MODEL,
        instruction=(
            "Review the news digest below.\n\n"
            "{raw_news_digest}\n\n"
            "Infer potential business, regulatory, or execution risks. "
            "Stay conservative — only flag risks with at least weak evidence in the digest. "
            "Maximum 5 bullet points."
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
            "Combine the inputs below into a concise markdown note for a downstream investment memo.\n\n"
            "## News Digest\n{raw_news_digest}\n\n"
            "## Sentiment Analysis\n{news_sentiment}\n\n"
            "## Risk Flags\n{news_risks}\n\n"
            "Write a summary section (3–4 sentences) followed by labelled Positives, Negatives, "
            "and Risk subsections. Keep it under 300 words total."
        ),
        output_key="final_news_note",
    )

    return SequentialAgent(
        name="news_pipeline",
        sub_agents=[fetch_agent, parallel_agents, synthesis_agent],
    )
