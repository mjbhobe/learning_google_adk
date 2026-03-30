from __future__ import annotations

import json
from typing import Any, Dict

import yfinance as yf
from logger import get_logger

logger = get_logger("retail_investment_copilot:market_data_service:tools")


def get_market_snapshot(ticker: str) -> Dict[str, Any]:
    logger.info(f"In market_data_service::get_market_snapshot() -> {ticker}")
    tk = yf.Ticker(ticker)
    info = tk.info or {}
    hist = tk.history(period="1y", interval="1d")
    # logger.info(f"market_data_service::get_market_snapshot(): i yr historu -> {info}")

    if hist.empty:
        ret_val = {"ticker": ticker, "error": "No market data returned by yfinance."}
        logger.info(f"Exiting market_data_service::get_market_snapshot() -> {ret_val}")
        return ret_val

    close = hist["Close"].dropna()
    returns = close.pct_change().dropna()
    # logger.info(f"market_data_service::get_market_snapshot(): close -> {close}")
    # logger.info(f"market_data_service::get_market_snapshot(): returns -> {returns}")

    snapshot = {
        "ticker": ticker,
        "company_name": info.get("longName") or info.get("shortName") or ticker,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "currency": info.get("currency"),
        "market_cap": info.get("marketCap"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "price_to_book": info.get("priceToBook"),
        "dividend_yield": info.get("dividendYield"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "return_on_equity": info.get("returnOnEquity"),
        "debt_to_equity": info.get("debtToEquity"),
        "current_price": float(close.iloc[-1]),
        "52w_change_pct": round(((close.iloc[-1] / close.iloc[0]) - 1) * 100, 2),
        "daily_volatility_pct": round(float(returns.std() * 100), 2)
        if not returns.empty
        else None,
        "avg_volume": int(hist["Volume"].tail(60).mean())
        if "Volume" in hist.columns
        else None,
        "sma_50": round(float(close.tail(50).mean()), 2),
        "sma_200": round(float(close.tail(200).mean()), 2),
        "price_vs_sma50_pct": round(
            (float(close.iloc[-1]) / float(close.tail(50).mean()) - 1) * 100, 2
        ),
        "price_vs_sma200_pct": round(
            (float(close.iloc[-1]) / float(close.tail(200).mean()) - 1) * 100, 2
        ),
    }
    logger.info(f"market_data_service::get_market_snapshot(): snapshot -> {snapshot}")
    return snapshot


def render_market_snapshot(ticker: str) -> str:
    snapshot = get_market_snapshot(ticker)
    return json.dumps(snapshot, indent=2, default=str)
