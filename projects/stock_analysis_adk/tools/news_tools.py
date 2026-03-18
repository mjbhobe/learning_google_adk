from __future__ import annotations

import datetime as dt
from urllib.parse import quote_plus

import feedparser
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from stock_analysis_adk.config import MAX_HEADLINES
from stock_analysis_adk.tools.market_data_tools import fetch_news


def fetch_google_news(symbol: str, company_name: str | None = None) -> list[dict]:
    query = quote_plus(company_name or symbol)
    url = f"https://news.google.com/rss/search?q={query}%20stock%20when:30d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:MAX_HEADLINES]:
        items.append({
            "title": entry.get("title", ""),
            "publisher": entry.get("source", {}).get("title", "Google News"),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return items


def fetch_yahoo_news(symbol: str) -> list[dict]:
    items = []
    raw = fetch_news(symbol)
    if not isinstance(raw, list):
        return items
    for entry in raw[:MAX_HEADLINES]:
        content = entry.get("content") or {}
        items.append({
            "title": content.get("title") or entry.get("title", ""),
            "publisher": content.get("provider", {}).get("displayName", "Yahoo Finance"),
            "link": content.get("canonicalUrl", {}).get("url", ""),
            "published": content.get("pubDate", ""),
        })
    return items


def build_sentiment_payload(symbol: str, company_name: str | None = None) -> dict:
    analyzer = SentimentIntensityAnalyzer()
    headlines = fetch_yahoo_news(symbol) + fetch_google_news(symbol, company_name)
    dedup = []
    seen = set()
    for item in headlines:
        key = item["title"].strip().lower()
        if key and key not in seen:
            seen.add(key)
            dedup.append(item)

    scored = []
    for item in dedup[:MAX_HEADLINES]:
        score = analyzer.polarity_scores(item["title"])
        scored.append({**item, **score})

    if scored:
        avg_compound = sum(x["compound"] for x in scored) / len(scored)
    else:
        avg_compound = 0.0

    sentiment_label = "positive" if avg_compound > 0.15 else "negative" if avg_compound < -0.15 else "neutral"

    topic_buckets = {
        "results": sum(1 for x in scored if any(k in x["title"].lower() for k in ["earnings", "revenue", "profit", "results"])),
        "products": sum(1 for x in scored if any(k in x["title"].lower() for k in ["launch", "product", "chip", "iphone", "cloud", "ai"])),
        "risk": sum(1 for x in scored if any(k in x["title"].lower() for k in ["lawsuit", "probe", "risk", "tariff", "ban", "recall"])),
        "m&a": sum(1 for x in scored if any(k in x["title"].lower() for k in ["acquire", "merger", "buyout", "stake"])),
    }

    return {
        "symbol": symbol,
        "headline_count": len(scored),
        "average_compound_sentiment": avg_compound,
        "sentiment_label": sentiment_label,
        "topic_buckets": topic_buckets,
        "headlines": scored[:12],
    }
