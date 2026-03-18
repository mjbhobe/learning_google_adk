from typing import Any
import yfinance as yf

from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai import types

from logger import get_logger

logger = get_logger("buffet_stock_analyser.utils")


def get_stock_info(symbol: str) -> (dict[str, Any], dict[str, Any]):
    """given a stock symbol (such as AAPL, RELIANCE.NS), extracts
    company information (company_name, sector, industry and description)
    and raw financial metrics (stock_price, roe, debt_to_equity, free_cash_flow,
    price_to_earnings_ratio, market_cap, beta)
    """
    logger.info(f"----- _get_stock_info() called for {symbol} -----")
    ticker = yf.Ticker(symbol)
    info = ticker.info

    # company information
    company_info = {
        "company_name": info.get("longName"),
        "sector": info.get("sector", "Unknown"),
        "industry": info.get("industry", "Unknown"),
        "description": info.get("longBusinessSummary", "No description available."),
    }
    logger.info(f"\n   company_info -> {company_info}\n")

    # raw financial metrics
    raw_financials = {
        "symbol": symbol,
        "stock_price": info.get("currentPrice"),
        "return_on_equity": info.get("returnOnEquity"),
        "debt_to_equity_ratio": info.get("debtToEquity", 0) / 100,  # Normalized
        "free_cash_flow": info.get("freeCashflow", 0),
        "price_to_earnings_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "beta": info.get("beta"),
    }
    logger.info(f"\n   raw_financials -> {raw_financials}\n")

    return company_info, raw_financials


async def run_agent_query(
    agent: Agent,
    session_service: InMemorySessionService,
    app_name: str,
    user_id: str,
    user_query: str,
    session: Session,
):
    logger.info(f"----- _run_agent_query() called for {user_query} -----")
    logger.info(f"\n     Session state -> {session.state}\n")

    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=app_name,
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_query)],
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=user_content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                # The final response is usually the last text part
                # console.print("\n[bold green]Agent Response:[/bold green]")
                # console.print(Markdown(event.content.parts[0].text))
                final_response = event.content.parts[0].text
                logger.debug(f"\n   final_response -> {final_response}\n")
                return final_response
