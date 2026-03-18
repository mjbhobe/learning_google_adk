from __future__ import annotations

import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from stock_analysis_adk.config import APP_NAME
from stock_analysis_adk.report_builder import build_markdown_report
from stock_analysis_adk.utils.logger import get_logger
from stock_analysis_adk.tools.business_tools import build_business_fundamentals_payload
from stock_analysis_adk.tools.metrics_tools import build_financial_payload
from stock_analysis_adk.tools.peer_tools import build_peer_payload
from stock_analysis_adk.tools.news_tools import build_sentiment_payload
from stock_analysis_adk.tools.market_data_tools import fetch_company_info

from stock_analysis_adk.agents.business_fundamentals_agent import (
    create_business_fundamentals_agent,
)
from stock_analysis_adk.agents.financial_analysis_agent import (
    create_financial_analysis_agent,
)
from stock_analysis_adk.agents.peer_benchmark_agent import create_peer_benchmark_agent
from stock_analysis_adk.agents.sentiment_analysis_agent import (
    create_sentiment_analysis_agent,
)
from stock_analysis_adk.agents.recommendation_agent import create_recommendation_agent


logger = get_logger(__name__)


async def _run_agent(agent, query: str) -> str:
    session_service = InMemorySessionService()
    user_id = "user"
    session_id = str(uuid.uuid4())
    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text or ""
            break
    return final_response_text.strip()


def _parallel_compute_raw(symbol: str) -> dict:
    company = fetch_company_info(symbol)
    company_name = company.get("longName") or company.get("shortName") or symbol
    with ThreadPoolExecutor(max_workers=4) as pool:
        future_business = pool.submit(build_business_fundamentals_payload, symbol)
        future_financial = pool.submit(build_financial_payload, symbol)
        future_peer = pool.submit(build_peer_payload, symbol)
        future_sentiment = pool.submit(build_sentiment_payload, symbol, company_name)

        return {
            "business": future_business.result(),
            "financial": future_financial.result(),
            "peer": future_peer.result(),
            "sentiment": future_sentiment.result(),
        }


async def _parallel_agent_analysis(symbol: str, raw_sections: dict) -> dict:
    business_agent = create_business_fundamentals_agent()
    financial_agent = create_financial_analysis_agent()
    peer_agent = create_peer_benchmark_agent()
    sentiment_agent = create_sentiment_analysis_agent()

    business_prompt = (
        f"Analyze the business fundamentals for {symbol}. "
        f"Use only this precomputed evidence pack and do not calculate anything:\n\n{raw_sections['business']}"
    )
    financial_prompt = (
        f"Analyze the financials for {symbol}. "
        f"Use only this precomputed metrics pack and do not calculate anything:\n\n{raw_sections['financial']}"
    )
    peer_prompt = (
        f"Analyze peer benchmarking for {symbol}. "
        f"Use only this precomputed peer comparison payload and do not calculate anything:\n\n{raw_sections['peer']}"
    )
    sentiment_prompt = (
        f"Analyze public-news sentiment for {symbol}. "
        f"Use only this precomputed sentiment payload and do not calculate anything:\n\n{raw_sections['sentiment']}"
    )

    results = await asyncio.gather(
        _run_agent(business_agent, business_prompt),
        _run_agent(financial_agent, financial_prompt),
        _run_agent(peer_agent, peer_prompt),
        _run_agent(sentiment_agent, sentiment_prompt),
    )

    return {
        "business": results[0],
        "financial": results[1],
        "peer": results[2],
        "sentiment": results[3],
    }


async def _final_recommendation(
    symbol: str, raw_sections: dict, agent_sections: dict
) -> str:
    recommendation_agent = create_recommendation_agent()
    prompt = f"""
Create the final recommendation for {symbol}.

Use only the following section outputs.
Do not invent facts.
Be explicit about the recommendation and the reasons.

Business analysis:
{agent_sections['business']}

Financial analysis:
{agent_sections['financial']}

Peer benchmarking:
{agent_sections['peer']}

Sentiment analysis:
{agent_sections['sentiment']}

Selected raw highlights:
- Financial python summary: {raw_sections['financial'].get('python_summary')}
- Peer comparison sample: {list(raw_sections['peer'].get('comparisons', {}).items())[:8]}
- Sentiment label: {raw_sections['sentiment'].get('sentiment_label')}
"""
    return await _run_agent(recommendation_agent, prompt)


def run_full_analysis(symbol: str) -> dict[str, Any]:
    logger.info("Starting analysis for %s", symbol)
    raw_sections = _parallel_compute_raw(symbol)
    agent_sections = asyncio.run(_parallel_agent_analysis(symbol, raw_sections))
    final_recommendation = asyncio.run(
        _final_recommendation(symbol, raw_sections, agent_sections)
    )
    report_markdown = build_markdown_report(
        symbol, raw_sections, agent_sections, final_recommendation
    )

    recommendation_line = (
        final_recommendation.splitlines()[0] if final_recommendation else "N/A"
    )
    peer_count = (
        raw_sections.get("peer", {}).get("peer_summary", {}).get("peer_count", 0)
    )
    news_count = raw_sections.get("sentiment", {}).get("headline_count", 0)

    return {
        "symbol": symbol,
        "raw_sections": raw_sections,
        "agent_sections": agent_sections,
        "final_recommendation": final_recommendation,
        "report_markdown": report_markdown,
        "summary": {
            "symbol": symbol,
            "peer_count": peer_count,
            "news_count": news_count,
            "recommendation": recommendation_line[:80],
        },
    }
