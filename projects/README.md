# ADK + Claude Sonnet Stock Analysis

This project implements a multi-agent stock analysis application using **Google ADK** and **Claude Sonnet via LiteLLM**.  
All downloads and calculations are done in straight Python. The LLM is used only to interpret precomputed metrics and produce the final Markdown report.

## What it does

For a given stock symbol, the app:

1. Downloads company profile, historical prices, financial statements, news, and (for U.S. companies) the latest 10-K filing.
2. Computes the analysis in Python:
   - Business fundamentals evidence pack
   - Financial ratio analysis
   - Peer benchmarking
   - News sentiment analysis
3. Runs ADK sub-agents in parallel to analyze each evidence pack.
4. Runs a final recommendation agent to produce an investment view.
5. Renders a structured Markdown report in CLI or Streamlit.

## ADK architecture

- `root_agent`: orchestration-friendly ADK composition
- Parallel sub-agents:
  - `business_fundamentals_agent`
  - `financial_analysis_agent`
  - `peer_benchmark_agent`
  - `sentiment_analysis_agent`
- Final sequential sub-agent:
  - `recommendation_agent`

The local application also uses a Python orchestrator to:
- minimize LLM tokens,
- keep all calculations deterministic,
- assemble a clean Markdown report.

## Project structure

```text
adk_stock_analysis/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── .env.example
└── stock_analysis_adk/
    ├── __init__.py
    ├── config.py
    ├── orchestrator.py
    ├── report_builder.py
    ├── agents/
    │   ├── __init__.py
    │   ├── model_factory.py
    │   ├── business_fundamentals_agent.py
    │   ├── financial_analysis_agent.py
    │   ├── peer_benchmark_agent.py
    │   ├── sentiment_analysis_agent.py
    │   ├── recommendation_agent.py
    │   └── root_agent.py
    ├── tools/
    │   ├── __init__.py
    │   ├── market_data_tools.py
    │   ├── filings_tools.py
    │   ├── metrics_tools.py
    │   ├── peer_tools.py
    │   ├── news_tools.py
    │   └── business_tools.py
    └── utils/
        ├── __init__.py
        ├── logger.py
        └── formatting.py
```

## Environment setup with uv (Python 3.14)

```bash
uv python install 3.14
uv venv .venv --python 3.14
source .venv/bin/activate
uv pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
uv python install 3.14
uv venv .venv --python 3.14
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

## Environment variables

Create a `.env` file from `.env.example`.

Required:

- `ANTHROPIC_API_KEY` — for Claude Sonnet
- `GOOGLE_GENAI_USE_VERTEXAI=False` — recommended for direct API usage with ADK + LiteLLM
- `ADK_MODEL=claude-sonnet-4-6` — default model used by the project

Optional:

- `SEC_COMPANY_NAME` — the company name/email required by `sec-edgar-downloader`, for example:
  `Your Name your.email@example.com`

Example `.env`:

```env
ANTHROPIC_API_KEY=your_key_here
GOOGLE_GENAI_USE_VERTEXAI=False
ADK_MODEL=claude-sonnet-4-6
SEC_COMPANY_NAME=Your Name your.email@example.com
```

## Run from the command line

```bash
python main.py --symbol AAPL
```

Save the report to a file:

```bash
python main.py --symbol MSFT --output reports/msft_report.md
```

## Run the Streamlit app

```bash
streamlit run app.py
```

## Notes

- U.S. 10-K downloading works best for U.S.-listed companies.
- Peer discovery uses a free public universe (S&P 500 + Nasdaq-100 + Dow) collected from Wikipedia tables and then filters by sector/industry + market-cap proximity.
- The app intentionally keeps payloads compact before calling the LLM to reduce token usage.
