# Retail Investment Research Copilot

A realistic hobby-developer project for the investment space that demonstrates **Google ADK (2026 stable)** with **Claude Sonnet 4.6** via **LiteLLM**.

## Why this project is business-relevant

Business users such as relationship managers, independent financial advisors, wealth desk analysts, or serious retail investors often need a fast first-pass investment memo. 

They often struggle with:

- Pulling together fundamentals, price behavior, and news in one place,
- Separating facts from narrative,
- Documenting a recommendation clearly,
- Producing something repeatable for multiple stocks.

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

## (Almost) Free/local-friendly tech stack

- yfinance
- RSS feeds via `feedparser`
- FastAPI + uvicorn
- Streamlit
- Google ADK
- Anthropic Claude through LiteLLM*

*(You'll need an Anthropic account and pre-load some $$ to access the Claude API - see [Claude Billing](https://platform.claude.com/settings/billing))

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
