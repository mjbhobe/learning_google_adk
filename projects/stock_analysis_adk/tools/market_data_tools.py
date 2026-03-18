from __future__ import annotations

import pandas as pd
import yfinance as yf
from typing import Any, Dict

from stock_analysis_adk.config import PRICE_HISTORY_PERIOD


def get_ticker(symbol: str) -> yf.Ticker:
    return yf.Ticker(symbol)


def fetch_company_info(symbol: str) -> dict:
    info = get_ticker(symbol).info or {}
    keep = [
        "symbol", "shortName", "longName", "sector", "industry", "country", "website",
        "longBusinessSummary", "marketCap", "enterpriseValue", "currentPrice",
        "trailingPE", "forwardPE", "priceToBook", "priceToSalesTrailing12Months",
        "ebitda", "trailingEps", "returnOnEquity", "returnOnAssets", "beta",
        "dividendYield", "profitMargins", "operatingMargins", "grossMargins"
    ]
    return {k: info.get(k) for k in keep}


def fetch_history(symbol: str, period: str = PRICE_HISTORY_PERIOD) -> pd.DataFrame:
    hist = get_ticker(symbol).history(period=period, auto_adjust=False)
    return hist


def fetch_financial_statements(symbol: str) -> Dict[str, pd.DataFrame]:
    t = get_ticker(symbol)
    bundle = {
        "income_stmt": t.income_stmt.copy(),
        "balance_sheet": t.balance_sheet.copy(),
        "cashflow": t.cashflow.copy(),
        "quarterly_income_stmt": t.quarterly_income_stmt.copy(),
    }
    return bundle


def fetch_news(symbol: str) -> list[dict]:
    t = get_ticker(symbol)
    news = getattr(t, "news", None)
    return news if isinstance(news, list) else {}
