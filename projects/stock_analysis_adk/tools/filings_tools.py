from __future__ import annotations

import os
import re
from pathlib import Path
from sec_edgar_downloader import Downloader

from stock_analysis_adk.config import SEC_COMPANY_NAME


SECTION_PATTERNS = {
    "business": (r"item\s+1\.?\s+business", r"item\s+1a\.?\s+risk\s+factors"),
    "risk_factors": (r"item\s+1a\.?\s+risk\s+factors", r"item\s+1b\.?\s+unresolved"),
    "md_and_a": (r"item\s+7\.?\s+management[’']?s?\s+discussion", r"item\s+7a\.?\s+quantitative"),
}


def _clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_between(text: str, start_pat: str, end_pat: str, max_chars: int = 12000) -> str:
    lower = text.lower()
    start = re.search(start_pat, lower, re.IGNORECASE)
    end = re.search(end_pat, lower, re.IGNORECASE)
    if not start:
        return ""
    s = start.start()
    e = end.start() if end and end.start() > s else min(len(text), s + max_chars)
    return _clean_text(text[s:e])[:max_chars]


def download_latest_10k(symbol: str, dest_dir: str = "edgar_data") -> str | None:
    dl = Downloader(SEC_COMPANY_NAME, dest_dir)
    try:
        dl.get("10-K", symbol, amount=1)
    except Exception:
        return None

    base = Path(dest_dir) / "sec-edgar-filings" / symbol / "10-K"
    if not base.exists():
        return None
    filings = sorted(base.glob("*/*"))
    for filing_dir in reversed(filings):
        txt_files = list(filing_dir.glob("*.txt"))
        if txt_files:
            return str(txt_files[0])
    return None


def extract_10k_sections(symbol: str) -> dict:
    path = download_latest_10k(symbol)
    if not path:
        return {"filing_path": None, "business": "", "risk_factors": "", "md_and_a": ""}

    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    sections = {"filing_path": path}
    for key, (start_pat, end_pat) in SECTION_PATTERNS.items():
        sections[key] = _extract_between(text, start_pat, end_pat)
    return sections
