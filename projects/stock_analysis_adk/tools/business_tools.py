from __future__ import annotations

import re

from stock_analysis_adk.tools.market_data_tools import fetch_company_info
from stock_analysis_adk.tools.filings_tools import extract_10k_sections


KEYWORDS = {
    "moat": ["brand", "network effect", "switching costs", "ecosystem", "scale", "proprietary", "patent"],
    "revenue_concentration": ["major customer", "significant customer", "customer concentration", "single customer", "top customer"],
    "scalability": ["platform", "subscription", "recurring", "digital", "cloud", "automation", "software"],
    "longevity": ["long-term", "backlog", "pipeline", "recurring revenue", "installed base"],
}


def _top_sentences(text: str, keywords: list[str], limit: int = 8) -> list[str]:
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    ranked = []
    for s in sentences:
        score = sum(1 for kw in keywords if kw.lower() in s.lower())
        if score > 0:
            ranked.append((score, s.strip()))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in ranked[:limit]]


def build_business_fundamentals_payload(symbol: str) -> dict:
    info = fetch_company_info(symbol)
    filing_sections = extract_10k_sections(symbol)

    long_summary = info.get("longBusinessSummary") or ""
    business = filing_sections.get("business", "")
    risks = filing_sections.get("risk_factors", "")
    mdna = filing_sections.get("md_and_a", "")

    moat_evidence = _top_sentences(" ".join([long_summary, business, mdna]), KEYWORDS["moat"])
    concentration_evidence = _top_sentences(" ".join([business, risks, mdna]), KEYWORDS["revenue_concentration"])
    scalability_evidence = _top_sentences(" ".join([long_summary, business, mdna]), KEYWORDS["scalability"])
    longevity_evidence = _top_sentences(" ".join([long_summary, business, mdna]), KEYWORDS["longevity"])

    return {
        "symbol": symbol,
        "company_name": info.get("longName") or info.get("shortName") or symbol,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "website": info.get("website"),
        "company_summary": long_summary[:3000],
        "business_section_excerpt": business[:5000],
        "risk_factors_excerpt": risks[:4000],
        "md_and_a_excerpt": mdna[:4000],
        "python_signals": {
            "moat_evidence": moat_evidence,
            "revenue_concentration_evidence": concentration_evidence,
            "scalability_evidence": scalability_evidence,
            "longevity_evidence": longevity_evidence,
        },
    }
