from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd

from stock_analysis_adk.config import TOP_PEER_COUNT
from stock_analysis_adk.tools.market_data_tools import fetch_company_info
from stock_analysis_adk.tools.metrics_tools import build_financial_payload


def _download_large_cap_universe() -> list[str]:
    urls = [
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "https://en.wikipedia.org/wiki/Nasdaq-100",
        "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
    ]
    tickers = set()
    for url in urls:
        try:
            tables = pd.read_html(url)
        except Exception:
            continue
        for table in tables:
            cols = {str(c).lower(): c for c in table.columns}
            for key in ["symbol", "ticker", "ticker symbol"]:
                if key in cols:
                    for val in table[cols[key]].astype(str).tolist():
                        tickers.add(val.replace(".", "-").strip())
    return sorted(tickers)


def discover_peers(symbol: str, max_peers: int = TOP_PEER_COUNT) -> list[str]:
    target = fetch_company_info(symbol)
    sector = target.get("sector")
    industry = target.get("industry")
    target_cap = target.get("marketCap") or 0

    universe = _download_large_cap_universe()
    candidates = []
    for ticker in universe:
        if ticker == symbol:
            continue
        try:
            info = fetch_company_info(ticker)
        except Exception:
            continue
        if not info:
            continue
        if sector and info.get("sector") != sector:
            continue
        if industry and info.get("industry") != industry:
            continue
        mcap = info.get("marketCap") or 0
        distance = abs((mcap or 0) - target_cap)
        candidates.append((ticker, distance))

    candidates.sort(key=lambda x: x[1])
    return [ticker for ticker, _ in candidates[:max_peers]]


def _flatten_for_peer_stats(payload: dict) -> dict:
    return {
        "gross_margin_pct": payload["profitability"].get("gross_margin_pct"),
        "operating_margin_pct": payload["profitability"].get("operating_margin_pct"),
        "net_profit_margin_pct": payload["profitability"].get("net_profit_margin_pct"),
        "roe_pct": payload["profitability"].get("roe_pct"),
        "roa_pct": payload["profitability"].get("roa_pct"),
        "roce_pct": payload["profitability"].get("roce_pct"),
        "current_ratio": payload["liquidity"].get("current_ratio"),
        "quick_ratio": payload["liquidity"].get("quick_ratio"),
        "cash_ratio": payload["liquidity"].get("cash_ratio"),
        "debt_to_equity": payload["leverage"].get("debt_to_equity"),
        "interest_coverage": payload["leverage"].get("interest_coverage"),
        "asset_turnover": payload["efficiency"].get("asset_turnover"),
        "inventory_turnover": payload["efficiency"].get("inventory_turnover"),
        "trailing_pe": payload["valuation"].get("trailing_pe"),
        "price_to_book": payload["valuation"].get("price_to_book"),
        "price_to_sales": payload["valuation"].get("price_to_sales"),
        "ev_to_ebitda": payload["valuation"].get("ev_to_ebitda"),
        "revenue_cagr_pct": payload["performance_growth"].get("revenue_cagr_pct"),
        "ebit_cagr_pct": payload["performance_growth"].get("ebit_cagr_pct"),
        "net_income_cagr_pct": payload["performance_growth"].get("net_income_cagr_pct"),
    }


def build_peer_payload(symbol: str) -> dict:
    peers = discover_peers(symbol)
    target_payload = build_financial_payload(symbol)

    rows = []
    for peer in peers:
        try:
            row = _flatten_for_peer_stats(build_financial_payload(peer))
            row["ticker"] = peer
            rows.append(row)
        except Exception:
            continue

    peer_df = pd.DataFrame(rows)
    if peer_df.empty:
        return {
            "symbol": symbol,
            "peers": [],
            "peer_summary": {},
            "comparisons": {},
        }

    metric_cols = [c for c in peer_df.columns if c != "ticker"]
    median_map = peer_df[metric_cols].median(numeric_only=True).to_dict()
    mean_map = peer_df[metric_cols].mean(numeric_only=True).to_dict()

    target_flat = _flatten_for_peer_stats(target_payload)
    comparisons = {}
    for metric, value in target_flat.items():
        peer_median = median_map.get(metric)
        if pd.isna(value) or pd.isna(peer_median):
            comparisons[metric] = {"company": value, "peer_median": peer_median, "delta_pct": np.nan, "position": "n/a"}
            continue
        delta_pct = ((value - peer_median) / abs(peer_median) * 100.0) if peer_median != 0 else np.nan
        comparisons[metric] = {
            "company": value,
            "peer_median": peer_median,
            "delta_pct": delta_pct,
            "position": "above" if value > peer_median else "below" if value < peer_median else "inline",
        }

    return {
        "symbol": symbol,
        "peers": peers,
        "peer_summary": {
            "peer_count": len(peers),
            "peer_mean": mean_map,
            "peer_median": median_map,
        },
        "comparisons": comparisons,
    }
