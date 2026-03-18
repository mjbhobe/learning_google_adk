from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from stock_analysis_adk.tools.market_data_tools import fetch_company_info, fetch_financial_statements


def _col_values(df: pd.DataFrame, row_name: str) -> list[float]:
    if df is None or df.empty or row_name not in df.index:
        return []
    series = pd.to_numeric(df.loc[row_name], errors="coerce")
    return [float(x) for x in series.tolist() if pd.notna(x)]


def _latest(df: pd.DataFrame, row_name: str, default=np.nan) -> float:
    vals = _col_values(df, row_name)
    return vals[0] if vals else default


def _avg(a: float, b: float) -> float:
    vals = [x for x in [a, b] if pd.notna(x)]
    return sum(vals)/len(vals) if vals else np.nan


def _growth_rates(values: list[float]) -> list[float]:
    out = []
    for i in range(len(values)-1):
        prev = values[i+1]
        curr = values[i]
        if prev in [0, None] or pd.isna(prev) or pd.isna(curr):
            out.append(np.nan)
        else:
            out.append((curr - prev) / abs(prev) * 100.0)
    return out


def _trend_label(values: list[float]) -> str:
    valid = [v for v in values if pd.notna(v)]
    if len(valid) < 2:
        return "insufficient data"
    if valid[0] > valid[-1]:
        return "improving"
    if valid[0] < valid[-1]:
        return "deteriorating"
    return "stable"


def _cagr(values: list[float]) -> float:
    valid = [v for v in values if pd.notna(v)]
    if len(valid) < 2 or valid[-1] == 0:
        return np.nan
    n = len(valid) - 1
    if valid[0] <= 0 or valid[-1] <= 0:
        return np.nan
    return ((valid[0] / valid[-1]) ** (1/n) - 1) * 100.0


def build_financial_payload(symbol: str) -> dict:
    info = fetch_company_info(symbol)
    stmts = fetch_financial_statements(symbol)
    inc = stmts["income_stmt"]
    bs = stmts["balance_sheet"]
    cf = stmts["cashflow"]

    revenue_series = _col_values(inc, "Total Revenue")
    ebit_series = _col_values(inc, "EBIT")
    net_income_series = _col_values(inc, "Net Income")
    eps_ttm = info.get("trailingEps", np.nan)

    current_assets = _latest(bs, "Current Assets")
    inventory = _latest(bs, "Inventory", 0.0)
    cash = _latest(bs, "Cash And Cash Equivalents", _latest(bs, "Cash", np.nan))
    current_liabilities = _latest(bs, "Current Liabilities")
    total_assets = _latest(bs, "Total Assets")
    total_liabilities = _latest(bs, "Total Liabilities Net Minority Interest", _latest(bs, "Total Liab"))
    equity = _latest(bs, "Stockholders Equity", _latest(bs, "Total Stockholder Equity"))
    invested_capital = equity + _latest(bs, "Long Term Debt", 0.0)

    cogs = _latest(inc, "Cost Of Revenue")
    operating_income = _latest(inc, "Operating Income", _latest(inc, "EBIT"))
    gross_profit = _latest(inc, "Gross Profit")
    interest_expense = abs(_latest(inc, "Interest Expense", np.nan))
    operating_cf = _latest(cf, "Operating Cash Flow", _latest(cf, "Total Cash From Operating Activities"))
    capex = abs(_latest(cf, "Capital Expenditure", _latest(cf, "Capital Expenditures", 0.0)))
    fcf = operating_cf - capex if pd.notna(operating_cf) and pd.notna(capex) else np.nan

    revenue = revenue_series[0] if revenue_series else np.nan
    ebit = ebit_series[0] if ebit_series else operating_income
    net_income = net_income_series[0] if net_income_series else np.nan

    profitability = {
        "gross_margin_pct": (gross_profit / revenue * 100.0) if revenue else np.nan,
        "operating_margin_pct": (operating_income / revenue * 100.0) if revenue else np.nan,
        "net_profit_margin_pct": (net_income / revenue * 100.0) if revenue else np.nan,
        "roe_pct": (net_income / equity * 100.0) if equity else np.nan,
        "roa_pct": (net_income / total_assets * 100.0) if total_assets else np.nan,
        "roce_pct": (ebit / invested_capital * 100.0) if invested_capital else np.nan,
    }

    liquidity = {
        "current_ratio": (current_assets / current_liabilities) if current_liabilities else np.nan,
        "quick_ratio": ((current_assets - inventory) / current_liabilities) if current_liabilities else np.nan,
        "cash_ratio": (cash / current_liabilities) if current_liabilities else np.nan,
    }

    leverage = {
        "debt_to_equity": (total_liabilities / equity) if equity else np.nan,
        "interest_coverage": (ebit / interest_expense) if interest_expense else np.nan,
    }

    efficiency = {
        "asset_turnover": (revenue / total_assets) if total_assets else np.nan,
        "inventory_turnover": (cogs / inventory) if inventory else np.nan,
    }

    valuation = {
        "trailing_pe": info.get("trailingPE", np.nan),
        "forward_pe": info.get("forwardPE", np.nan),
        "price_to_book": info.get("priceToBook", np.nan),
        "price_to_sales": info.get("priceToSalesTrailing12Months", np.nan),
        "ev_to_ebitda": (info.get("enterpriseValue", np.nan) / info.get("ebitda", np.nan))
            if info.get("enterpriseValue") and info.get("ebitda") else np.nan,
        "dividend_yield_pct": (info.get("dividendYield", np.nan) or np.nan) * 100.0
            if info.get("dividendYield") is not None else np.nan,
    }

    performance_growth = {
        "revenue_growth_yoy_pct": _growth_rates(revenue_series)[:4],
        "ebit_growth_yoy_pct": _growth_rates(ebit_series)[:4],
        "net_income_growth_yoy_pct": _growth_rates(net_income_series)[:4],
        "revenue_cagr_pct": _cagr(revenue_series[:5]),
        "ebit_cagr_pct": _cagr(ebit_series[:5]),
        "net_income_cagr_pct": _cagr(net_income_series[:5]),
        "free_cash_flow": fcf,
        "eps_ttm": eps_ttm,
    }

    python_summary = {
        "profitability_trend": _trend_label([profitability["operating_margin_pct"], profitability["net_profit_margin_pct"]]),
        "growth_trend": _trend_label([x for x in performance_growth["revenue_growth_yoy_pct"] if pd.notna(x)] or [np.nan]),
        "leverage_view": "elevated" if leverage["debt_to_equity"] and leverage["debt_to_equity"] > 2 else "moderate",
        "liquidity_view": "strong" if liquidity["current_ratio"] and liquidity["current_ratio"] >= 1.5 else "watch",
    }

    return {
        "symbol": symbol,
        "company": info.get("longName") or info.get("shortName") or symbol,
        "profitability": profitability,
        "liquidity": liquidity,
        "leverage": leverage,
        "efficiency": efficiency,
        "valuation": valuation,
        "performance_growth": performance_growth,
        "python_summary": python_summary,
    }
