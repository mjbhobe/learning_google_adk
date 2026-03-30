# .env.example

```
ANTHROPIC_API_KEY=your_anthropic_key_here
PYTHONUTF8=1
APP_NAME=retail_investment_research_copilot

```

# README.md

```
# Retail Investment Research Copilot

A realistic hobby-developer project for the investment space that demonstrates **Google ADK (2026 stable Python release)** with **Claude Sonnet 4.6** via **LiteLLM**.

## Why this project is business-relevant

Business users such as relationship managers, independent financial advisors, wealth desk analysts, or serious retail investors often need a fast first-pass investment memo. They struggle with:
- pulling together fundamentals, price behavior, and news in one place,
- separating facts from narrative,
- documenting a recommendation clearly,
- producing something repeatable for multiple stocks.

This project turns that messy workflow into a structured, agentic pipeline.

## ADK workflow design

The project showcases all three classic workflow agents:

1. **SequentialAgent**
   - Runs intake -> data preparation -> synthesis in a fixed order.
2. **ParallelAgent**
   - Runs fundamentals, technicals, and news/risk analysis concurrently.
3. **LoopAgent**
   - Critiques and refines the memo for a few iterations.

## Architecture

- `services/market_data_service`: fetches yfinance fundamentals and price-derived technical context.
- `services/news_service`: collects free RSS/news context.
- `services/memo_service`: synthesizes recommendation using ADK workflow agents.
- `main.py`: console driver.
- `streamlit_app.py`: UI driver.
- Inter-service communication is plain JSON over HTTP using `requests`.
- We intentionally avoid A2A here because the goal is clarity and local hackability.

## Workflow

1. User enters stock ticker and investment horizon.
2. `main.py` or `streamlit_app.py` calls:
   - market-data service
   - news service
3. Orchestrator sends combined JSON to memo service.
4. Memo service runs:
   - Sequential intake
   - Parallel sub-analysis
   - Sequential synthesis
   - Loop-based critique and rewrite
5. Final markdown report is returned.

## Free/local-friendly stack

- yfinance
- RSS feeds via `feedparser`
- FastAPI + uvicorn
- Streamlit
- Google ADK
- Anthropic Claude through LiteLLM

## UV setup

```bash
uv venv
uv sync
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONUTF8="1"
Copy-Item .env.example .env
```

On macOS/Linux:

```bash
source .venv/bin/activate
export PYTHONUTF8=1
cp .env.example .env
```

## Start services

```bash
uv run python scripts/start_services.py
```

## Run console driver

```bash
uv run python main.py
```

## Run Streamlit

```bash
uv run streamlit run streamlit_app.py
```

## Suggested demo tickers

- MSFT
- AAPL
- TCS.NS
- INFY.NS
- RELIANCE.NS

## Caveats

- This is an educational demo, not investment advice.
- Free data can be delayed, missing, or inconsistent.
- The memo is only as good as the input data.

```

# blog.md

```
# Building a Retail Investment Research Copilot with Google ADK and Claude Sonnet 4.6

## Why I built this

Most retail investing tools are either too shallow or too opaque. You get dashboards full of ratios, but not a defensible memo. Or you get AI-generated opinions without transparent inputs.

I wanted a middle path:
- pull in free market data,
- run specialized analyses in parallel,
- synthesize the findings in a structured way,
- then force the system to critique its own output.

That makes this project a great fit for the **Google Agent Development Kit (ADK)** workflow model.

## The business problem

Investment professionals and advanced retail investors repeatedly perform the same tasks:
- gather financial context,
- check price behavior,
- scan recent news,
- form a view,
- write a note.

The process is time-consuming and highly repetitive.

## Why ADK is a good fit

This project uses:
- **SequentialAgent** for deterministic control flow,
- **ParallelAgent** for concurrent specialist analysis,
- **LoopAgent** for memo refinement.

## Service split

I deliberately split the project into small locally hosted services:
- a market data service,
- a news service,
- a memo service.

This makes the architecture look and feel like a “real” internal platform, while staying runnable on a home laptop.

## What makes the demo persuasive

The final output is not just a chat response. It is a markdown investment memo with:
- business summary,
- upside and downside drivers,
- key metrics,
- technical context,
- recent news implications,
- final stance.

That is much closer to what a business user actually values.

## Key lesson

ADK becomes especially compelling when you stop thinking in terms of “one giant super-agent” and instead design a workflow:
- deterministic steps where you need control,
- parallel specialists where you need speed,
- looped refinement where quality matters.

That is exactly what this project demonstrates.

```

# main.py

```
import requests

MARKET_DATA_URL = "http://127.0.0.1:8101/invoke"
NEWS_URL = "http://127.0.0.1:8102/invoke"
MEMO_URL = "http://127.0.0.1:8103/invoke"

def main() -> None:
    print("Retail Investment Research Copilot")
    ticker = input("Enter ticker (example: MSFT or TCS.NS): ").strip()
    horizon = input("Investment horizon (example: 3 years): ").strip() or "3 years"
    risk = input("Risk appetite (low/medium/high): ").strip() or "medium"

    market_resp = requests.post(MARKET_DATA_URL, json={"payload": {"ticker": ticker}})
    news_resp = requests.post(NEWS_URL, json={"payload": {"ticker": ticker}})
    market_resp.raise_for_status()
    news_resp.raise_for_status()

    combined_payload = {
        "ticker": ticker,
        "horizon": horizon,
        "risk_appetite": risk,
        "market_data": market_resp.json()["result"],
        "news_analysis": news_resp.json()["result"],
    }

    memo_resp = requests.post(MEMO_URL, json={"payload": combined_payload})
    memo_resp.raise_for_status()
    print("\n" + memo_resp.json()["result"])

if __name__ == "__main__":
    main()

```

# pyproject.toml

```
[project]
name = "retail-investment-research-copilot"
version = "0.1.0"
description = "ADK 2026 retail investment research copilot using Claude Sonnet via LiteLLM"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "google-adk==1.25.1",
  "litellm>=1.74.0",
  "anthropic>=0.50.0",
  "fastapi>=0.115.0",
  "uvicorn>=0.34.0",
  "requests>=2.32.0",
  "streamlit>=1.44.0",
  "pandas>=2.2.0",
  "numpy>=2.1.0",
  "yfinance>=0.2.58",
  "feedparser>=6.0.11",
  "python-dotenv>=1.1.0",
  "pydantic>=2.10.0"
]

[tool.uv]
dev-dependencies = []

```

# sample_inputs/demo_request.json

```
{
  "ticker": "MSFT",
  "horizon": "3 years",
  "risk_appetite": "medium"
}

```

# scripts/start_services.py

```
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SERVICES = [
    ("market-data-service", "services.market_data_service.service_app", 8101),
    ("news-service", "services.news_service.service_app", 8102),
    ("memo-service", "services.memo_service.service_app", 8103),
]

def main() -> None:
    processes = []
    try:
        for name, module, port in SERVICES:
            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                f"{module}:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--reload",
            ]
            print(f"Starting {name} on port {port}...")
            processes.append(subprocess.Popen(cmd, cwd=ROOT))
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        for proc in processes:
            proc.kill()

if __name__ == "__main__":
    main()

```

# services/__init__.py

```


```

# services/market_data_service/__init__.py

```


```

# services/market_data_service/agent.py

```
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm
from .tools import render_market_snapshot

MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")

def build_root_agent():
    intake_agent = LlmAgent(
        name="ticker_intake",
        model=MODEL,
        instruction=(
            "You receive a user prompt containing a stock ticker. "
            "Extract the ticker symbol, normalize it if needed, and restate the request in one concise line."
        ),
        output_key="normalized_request",
    )

    snapshot_agent = LlmAgent(
        name="fundamental_and_technical_analyst",
        model=MODEL,
        tools=[render_market_snapshot],
        instruction=(
            "Use the render_market_snapshot tool to fetch a free market snapshot. "
            "Then produce a compact markdown section with key fundamentals and technical context. "
            "Be factual and mention obvious data quality gaps."
        ),
        output_key="market_snapshot_summary",
    )

    interpretation_agent = LlmAgent(
        name="signal_interpreter",
        model=MODEL,
        instruction=(
            "Interpret the market snapshot already available in state. "
            "Discuss valuation, trend posture, volatility, and balance-sheet quality in simple language."
        ),
        output_key="market_interpretation",
    )

    parallel_research = ParallelAgent(
        name="parallel_market_research",
        sub_agents=[snapshot_agent, interpretation_agent],
    )

    final_agent = LlmAgent(
        name="market_data_packager",
        model=MODEL,
        instruction=(
            "Create a market-data summary for the downstream memo service. "
            "Combine normalized request, market snapshot summary, and market interpretation into one markdown note."
        ),
        output_key="final_market_data_note",
    )

    return SequentialAgent(
        name="market_data_pipeline",
        sub_agents=[intake_agent, parallel_research, final_agent],
    )

```

# services/market_data_service/models.py

```
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class AgentRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    prompt: Optional[str] = None


class AgentResponse(BaseModel):
    status: str = "ok"
    result: str
    meta: Dict[str, Any] = Field(default_factory=dict)

```

# services/market_data_service/runtime.py

```
import asyncio
import os
import uuid
from typing import Any, Dict, Optional

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types


def flatten_text_from_event(event: Any) -> str:
    """Best-effort text extraction from an ADK event."""
    content = getattr(event, "content", None)
    if not content:
        return ""
    parts = getattr(content, "parts", None) or []
    chunks: list[str] = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)
    return "\n".join(chunks).strip()


async def run_agent_async(agent: Any, prompt: str, initial_state: Optional[Dict[str, Any]] = None) -> str:
    """Run an ADK agent in-process and return the final text response."""
    app_name = os.getenv("APP_NAME", "local_adk_app")
    user_id = os.getenv("ADK_USER_ID", "demo_user")
    session_service = InMemorySessionService()
    runner = InMemoryRunner(agent=agent, app_name=app_name, session_service=session_service)

    session = await runner.session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state or {},
        session_id=str(uuid.uuid4()),
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=user_message,
        ):
            text = flatten_text_from_event(event)
            if text:
                final_text = text
    finally:
        await runner.close()

    return final_text


def run_agent(agent: Any, prompt: str, initial_state: Optional[Dict[str, Any]] = None) -> str:
    return asyncio.run(run_agent_async(agent=agent, prompt=prompt, initial_state=initial_state))

```

# services/market_data_service/service_app.py

```
from fastapi import FastAPI
from .agent import build_root_agent
from .models import AgentRequest, AgentResponse
from .runtime import run_agent

app = FastAPI(title="Market Data Service")

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "market_data_service"}

@app.post("/invoke", response_model=AgentResponse)
def invoke(req: AgentRequest) -> AgentResponse:
    agent = build_root_agent()
    if req.prompt:
        prompt = req.prompt
    else:
        prompt = "Analyze this JSON payload and produce the required result:\n\n" + str(req.payload)
    result = run_agent(agent=agent, prompt=prompt, initial_state={"input_payload": req.payload})
    return AgentResponse(result=result, meta={"service": "market_data_service"})

```

# services/market_data_service/tools.py

```
from __future__ import annotations
import json
from typing import Dict, Any
import yfinance as yf


def get_market_snapshot(ticker: str) -> Dict[str, Any]:
    tk = yf.Ticker(ticker)
    info = tk.info or {}
    hist = tk.history(period="1y", interval="1d")

    if hist.empty:
        return {"ticker": ticker, "error": "No market data returned by yfinance."}

    close = hist["Close"].dropna()
    returns = close.pct_change().dropna()

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
        "daily_volatility_pct": round(float(returns.std() * 100), 2) if not returns.empty else None,
        "avg_volume": int(hist["Volume"].tail(60).mean()) if "Volume" in hist.columns else None,
        "sma_50": round(float(close.tail(50).mean()), 2),
        "sma_200": round(float(close.tail(200).mean()), 2),
        "price_vs_sma50_pct": round((float(close.iloc[-1]) / float(close.tail(50).mean()) - 1) * 100, 2),
        "price_vs_sma200_pct": round((float(close.iloc[-1]) / float(close.tail(200).mean()) - 1) * 100, 2),
    }
    return snapshot


def render_market_snapshot(ticker: str) -> str:
    snapshot = get_market_snapshot(ticker)
    return json.dumps(snapshot, indent=2, default=str)

```

# services/memo_service/__init__.py

```


```

# services/memo_service/agent.py

```
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")

def build_root_agent():
    intake_agent = LlmAgent(
        name="memo_intake",
        model=MODEL,
        instruction=(
            "Read the JSON payload. Extract ticker, horizon, risk appetite, market data note, and news note. "
            "Create a clean internal brief for specialist agents."
        ),
        output_key="research_brief",
    )

    valuation_agent = LlmAgent(
        name="valuation_specialist",
        model=MODEL,
        instruction=(
            "Using the research brief, explain whether the stock looks obviously cheap, fair, or expensive. "
            "Do not fabricate ratios beyond what is present."
        ),
        output_key="valuation_view",
    )

    momentum_agent = LlmAgent(
        name="momentum_specialist",
        model=MODEL,
        instruction=(
            "Using the research brief, explain what the price trend and volatility imply for the selected horizon."
        ),
        output_key="momentum_view",
    )

    risk_agent = LlmAgent(
        name="risk_specialist",
        model=MODEL,
        instruction=(
            "Using the research brief, identify the most important downside risks and uncertainties."
        ),
        output_key="risk_view",
    )

    parallel_stage = ParallelAgent(
        name="parallel_specialist_stage",
        sub_agents=[valuation_agent, momentum_agent, risk_agent],
    )

    writer_agent = LlmAgent(
        name="memo_writer",
        model=MODEL,
        instruction=(
            "Write a business-friendly markdown investment memo with these sections: "
            "Company snapshot, Bull case, Bear case, What the market data says, What the news says, "
            "Decision stance, and What would change my mind. "
            "End with one of: Watchlist / Hold / Accumulate / Avoid. "
            "This is educational, not investment advice."
        ),
        output_key="draft_memo",
    )

    critic_agent = LlmAgent(
        name="memo_critic",
        model=MODEL,
        instruction=(
            "Critique the draft memo in state. Check clarity, internal consistency, unsupported claims, "
            "and whether the recommendation matches the evidence. Produce actionable rewrite guidance."
        ),
        output_key="memo_critique",
    )

    rewriter_agent = LlmAgent(
        name="memo_rewriter",
        model=MODEL,
        instruction=(
            "Rewrite the memo using the critique in state. Improve structure, reduce overclaiming, "
            "and tighten the final recommendation."
        ),
        output_key="draft_memo",
    )

    refinement_loop = LoopAgent(
        name="memo_refinement_loop",
        sub_agents=[critic_agent, rewriter_agent],
        max_iterations=2,
    )

    finalizer = LlmAgent(
        name="finalizer",
        model=MODEL,
        instruction=(
            "Return the final markdown memo from state. Preserve headings and make it readable."
        ),
        output_key="final_memo",
    )

    return SequentialAgent(
        name="memo_pipeline",
        sub_agents=[intake_agent, parallel_stage, writer_agent, refinement_loop, finalizer],
    )

```

# services/memo_service/models.py

```
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class AgentRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    prompt: Optional[str] = None


class AgentResponse(BaseModel):
    status: str = "ok"
    result: str
    meta: Dict[str, Any] = Field(default_factory=dict)

```

# services/memo_service/runtime.py

```
import asyncio
import os
import uuid
from typing import Any, Dict, Optional

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types


def flatten_text_from_event(event: Any) -> str:
    """Best-effort text extraction from an ADK event."""
    content = getattr(event, "content", None)
    if not content:
        return ""
    parts = getattr(content, "parts", None) or []
    chunks: list[str] = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)
    return "\n".join(chunks).strip()


async def run_agent_async(agent: Any, prompt: str, initial_state: Optional[Dict[str, Any]] = None) -> str:
    """Run an ADK agent in-process and return the final text response."""
    app_name = os.getenv("APP_NAME", "local_adk_app")
    user_id = os.getenv("ADK_USER_ID", "demo_user")
    session_service = InMemorySessionService()
    runner = InMemoryRunner(agent=agent, app_name=app_name, session_service=session_service)

    session = await runner.session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state or {},
        session_id=str(uuid.uuid4()),
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=user_message,
        ):
            text = flatten_text_from_event(event)
            if text:
                final_text = text
    finally:
        await runner.close()

    return final_text


def run_agent(agent: Any, prompt: str, initial_state: Optional[Dict[str, Any]] = None) -> str:
    return asyncio.run(run_agent_async(agent=agent, prompt=prompt, initial_state=initial_state))

```

# services/memo_service/service_app.py

```
from fastapi import FastAPI
from .agent import build_root_agent
from .models import AgentRequest, AgentResponse
from .runtime import run_agent

app = FastAPI(title="Memo Service")

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "memo_service"}

@app.post("/invoke", response_model=AgentResponse)
def invoke(req: AgentRequest) -> AgentResponse:
    agent = build_root_agent()
    if req.prompt:
        prompt = req.prompt
    else:
        prompt = "Analyze this JSON payload and produce the required result:\n\n" + str(req.payload)
    result = run_agent(agent=agent, prompt=prompt, initial_state={"input_payload": req.payload})
    return AgentResponse(result=result, meta={"service": "memo_service"})

```

# services/news_service/__init__.py

```


```

# services/news_service/agent.py

```
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm
from .tools import fetch_rss_news

MODEL = LiteLlm(model="anthropic/claude-sonnet-4-6")

def build_root_agent():
    fetch_agent = LlmAgent(
        name="news_fetcher",
        model=MODEL,
        tools=[fetch_rss_news],
        instruction=(
            "Use the fetch_rss_news tool with the stock ticker found in the user prompt. "
            "Return a concise news digest and do not invent headlines."
        ),
        output_key="raw_news_digest",
    )

    sentiment_agent = LlmAgent(
        name="news_sentiment_analyst",
        model=MODEL,
        instruction=(
            "Analyze the raw news digest in state. "
            "Identify 3 to 5 positives, negatives, and uncertain items affecting the company."
        ),
        output_key="news_sentiment",
    )

    risk_agent = LlmAgent(
        name="news_risk_analyst",
        model=MODEL,
        instruction=(
            "Review the raw news digest in state and infer potential business, regulatory, or execution risks. "
            "Stay conservative when evidence is weak."
        ),
        output_key="news_risks",
    )

    parallel_agents = ParallelAgent(
        name="parallel_news_review",
        sub_agents=[sentiment_agent, risk_agent],
    )

    synthesis_agent = LlmAgent(
        name="news_synthesis",
        model=MODEL,
        instruction=(
            "Combine the raw news digest, sentiment view, and risk view into a concise markdown note "
            "for a downstream investment memo."
        ),
        output_key="final_news_note",
    )

    return SequentialAgent(
        name="news_pipeline",
        sub_agents=[fetch_agent, parallel_agents, synthesis_agent],
    )

```

# services/news_service/models.py

```
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class AgentRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    prompt: Optional[str] = None


class AgentResponse(BaseModel):
    status: str = "ok"
    result: str
    meta: Dict[str, Any] = Field(default_factory=dict)

```

# services/news_service/runtime.py

```
import asyncio
import os
import uuid
from typing import Any, Dict, Optional

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types


def flatten_text_from_event(event: Any) -> str:
    """Best-effort text extraction from an ADK event."""
    content = getattr(event, "content", None)
    if not content:
        return ""
    parts = getattr(content, "parts", None) or []
    chunks: list[str] = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)
    return "\n".join(chunks).strip()


async def run_agent_async(agent: Any, prompt: str, initial_state: Optional[Dict[str, Any]] = None) -> str:
    """Run an ADK agent in-process and return the final text response."""
    app_name = os.getenv("APP_NAME", "local_adk_app")
    user_id = os.getenv("ADK_USER_ID", "demo_user")
    session_service = InMemorySessionService()
    runner = InMemoryRunner(agent=agent, app_name=app_name, session_service=session_service)

    session = await runner.session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state or {},
        session_id=str(uuid.uuid4()),
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=user_message,
        ):
            text = flatten_text_from_event(event)
            if text:
                final_text = text
    finally:
        await runner.close()

    return final_text


def run_agent(agent: Any, prompt: str, initial_state: Optional[Dict[str, Any]] = None) -> str:
    return asyncio.run(run_agent_async(agent=agent, prompt=prompt, initial_state=initial_state))

```

# services/news_service/service_app.py

```
from fastapi import FastAPI
from .agent import build_root_agent
from .models import AgentRequest, AgentResponse
from .runtime import run_agent

app = FastAPI(title="News Service")

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "news_service"}

@app.post("/invoke", response_model=AgentResponse)
def invoke(req: AgentRequest) -> AgentResponse:
    agent = build_root_agent()
    if req.prompt:
        prompt = req.prompt
    else:
        prompt = "Analyze this JSON payload and produce the required result:\n\n" + str(req.payload)
    result = run_agent(agent=agent, prompt=prompt, initial_state={"input_payload": req.payload})
    return AgentResponse(result=result, meta={"service": "news_service"})

```

# services/news_service/tools.py

```
from __future__ import annotations
import feedparser
import json
from urllib.parse import quote


def fetch_rss_news(ticker: str) -> str:
    query = quote(f"{ticker} stock")
    url = f"https://news.google.com/rss/search?q={query}"
    parsed = feedparser.parse(url)
    items = []
    for entry in parsed.entries[:8]:
        items.append({
            "title": getattr(entry, "title", ""),
            "link": getattr(entry, "link", ""),
            "published": getattr(entry, "published", ""),
            "summary": getattr(entry, "summary", ""),
        })
    return json.dumps(items, indent=2)

```

# streamlit_app.py

```
import requests
import streamlit as st

st.set_page_config(page_title="Investment Research Copilot", layout="wide")
st.title("Retail Investment Research Copilot")

ticker = st.text_input("Ticker", value="MSFT")
horizon = st.selectbox("Horizon", ["6 months", "1 year", "3 years", "5 years"], index=2)
risk = st.selectbox("Risk appetite", ["low", "medium", "high"], index=1)

if st.button("Generate memo"):
    with st.spinner("Calling local services..."):
        market_resp = requests.post("http://127.0.0.1:8101/invoke", json={"payload": {"ticker": ticker}})
        news_resp = requests.post("http://127.0.0.1:8102/invoke", json={"payload": {"ticker": ticker}})
        market_resp.raise_for_status()
        news_resp.raise_for_status()

        memo_payload = {
            "ticker": ticker,
            "horizon": horizon,
            "risk_appetite": risk,
            "market_data": market_resp.json()["result"],
            "news_analysis": news_resp.json()["result"],
        }
        memo_resp = requests.post("http://127.0.0.1:8103/invoke", json={"payload": memo_payload})
        memo_resp.raise_for_status()

    st.markdown(memo_resp.json()["result"])

```
