from __future__ import annotations

import json
from urllib.parse import quote

import feedparser
from logger import get_logger

logger = get_logger("retail_investment_copilot:news_service:tools")


def fetch_rss_news(ticker: str) -> str:
    logger.info(f"In news_service::fetch_rss_news() -> {ticker}")
    query = quote(f"{ticker} stock")
    url = f"https://news.google.com/rss/search?q={query}"
    parsed = feedparser.parse(url)
    items = []
    for entry in parsed.entries[:8]:
        items.append(
            {
                "title": getattr(entry, "title", ""),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", ""),
                "summary": getattr(entry, "summary", ""),
            }
        )
    ret_val = json.dumps(items, indent=2)
    logger.info(f"Exiting news_service::fetch_rss_news() -> {ret_val}")
    return ret_val
