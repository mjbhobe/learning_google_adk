from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "adk_stock_analysis"
DEFAULT_MODEL = os.getenv("ADK_MODEL", "claude-sonnet-4-6")
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "False")
SEC_COMPANY_NAME = os.getenv("SEC_COMPANY_NAME", "Research Team research@example.com")

TOP_PEER_COUNT = 10
PRICE_HISTORY_PERIOD = "5y"
MAX_HEADLINES = 15
