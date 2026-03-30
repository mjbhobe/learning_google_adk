# Building a Retail Investment Research Copilot with Google ADK and Claude Sonnet

*Orchestrating a multi-service agentic pipeline — market data, news, and memo writing — powered by Google's Agent Development Kit and Claude Sonnet.*

---

> **⚠️ DISCLAIMER — EDUCATIONAL PURPOSES ONLY**
>
> **This blog post and the accompanying project are for educational purposes only and must NOT be construed as financial advice or an investment recommendation of any kind. The sole purpose of this article is to demonstrate how multi-agent AI workflows can be constructed using a real-world use case with Google ADK. Past performance is not indicative of future results. If you are considering investing in any financial instrument, please seek advice from a qualified financial professional before making any investment decision. The author bears no responsibility for any financial decisions made based on this content.**

---

## Introduction — The Problem with Retail Investment Research

Most retail investing tools sit at one of two extremes. On one end you get a dashboard full of ratios — PE, ROE, D/E — with no context or narrative. On the other end you get AI-generated opinions delivered as a single opaque chat response, with no transparency about what data drove the conclusion.

What a sophisticated retail investor actually needs is closer to what an equity research desk produces: a **structured investment memo** — a document that shows you what data was gathered, how specialist analysts interpreted it, and how those interpretations were synthesised into a defensible stance.

This project builds exactly that, using **Google ADK** (Agent Development Kit) to orchestrate a pipeline of specialised agents that run as independent microservices, talk to each other over HTTP, and collaboratively produce a polished markdown investment memo for any publicly traded stock.

For market and financial data we use the free `yfinance` library (Yahoo Finance). For news we scrape Google News RSS feeds. The user supplies a **stock ticker symbol** — for example `MSFT` (Microsoft), `AAPL` (Apple), `RELIANCE.NS` (Reliance Industries), `TCS.NS` (Tata Consultancy Services) — and the pipeline does the rest.

> **💡 Tip:** Navigate to [Yahoo! Finance](https://finance.yahoo.com/) and search for the company name. The dropdown will show you the correct ticker symbol to use.

---

## Why Google ADK Is a Natural Fit

This project uses three of ADK's core orchestration primitives, each chosen deliberately:

| ADK Primitive | Where Used | Why |
|---|---|---|
| `SequentialAgent` | All three services (outer pipeline) | Guarantees deterministic left-to-right execution — intake → research → synthesis |
| `ParallelAgent` | Inside market-data and news services | Runs independent specialist agents concurrently for speed |
| `LoopAgent` | Memo service (refinement stage) | Runs a critic → rewriter loop N times to iteratively improve memo quality |

The key insight is that you stop thinking about "one giant super-agent" and instead design a **workflow**:
- Deterministic steps where you need control,
- Parallel specialists where you need speed,
- Looping refinement where output quality matters.

---

## High-Level Architecture

The application is split into three independent **FastAPI/Uvicorn microservices**, each wrapping its own ADK agent pipeline. The front-ends (`main.py` and `streamlit_app.py`) are thin HTTP clients — they know nothing about ADK, sessions, or runners.

```
   CLI (main.py)          Streamlit (streamlit_app.py)
         │                          │
         └──────────┬───────────────┘
                    │  1. POST /invoke  { ticker }
                    ▼
       ┌─────────────────────────────┐
       │  Market Data Service :8101  │  ← SequentialAgent
       │  (yfinance + LLM analysis)  │    [intake → parallel(snapshot,interpret) → packager]
       └─────────────────────────────┘
                    │ market_data_analysis (markdown note)
                    │  2. POST /invoke  { ticker }
                    ▼
       ┌─────────────────────────────┐
       │  News Service        :8102  │  ← SequentialAgent
       │  (Google News RSS)          │    [fetcher → parallel(sentiment,risk) → synthesis]
       └─────────────────────────────┘
                    │ news_analysis (markdown note)
                    │  3. POST /invoke  { ticker, horizon, risk, market_note, news_note }
                    ▼
       ┌─────────────────────────────┐
       │  Memo Service        :8103  │  ← SequentialAgent
       │  (parallel specialists      │    [intake → parallel(valuation,momentum,risk)
       │   + LoopAgent refinement)   │     → writer → loop(critic,rewriter) → finalizer]
       └─────────────────────────────┘
                    │
                    ▼
          { "result": "...markdown memo..." }
```

**Data flow summary:**

1. Both front-ends ask the user for a ticker, an investment horizon, and a risk appetite.
2. They call the **Market Data Service** (`POST /invoke`) to get a structured market analysis note.
3. They call the **News Service** (`POST /invoke`) to get a sentiment- and risk-annotated news digest.
4. Both notes, along with the user's horizon and risk inputs, are bundled into a single payload and sent to the **Memo Service** (`POST /invoke`).
5. The Memo Service's agent pipeline produces a polished, structured investment memo in Markdown.
6. The front-end renders the memo — in the terminal (via `rich`) for `main.py`, or in the browser (via `st.markdown`) for `streamlit_app.py`.

---

## Project File Structure

```
retail_investment_research_copilot/
├── .env                                   # API keys (not committed to git)
├── .env.example                           # Template for required keys
├── main.py                                # CLI entry point
├── streamlit_app.py                       # Streamlit web UI entry point
├── logger.py                              # Shared logging setup (Rich console)
├── pyproject.toml                         # Project metadata & dependencies (uv)
├── scripts/
│   └── start_services.py                  # Launches all three uvicorn services
└── agents/
    ├── __init__.py
    ├── market_data_service/
    │   ├── agent.py                       # SequentialAgent + ParallelAgent pipeline
    │   ├── tools.py                       # yfinance data fetching tool
    │   ├── runtime.py                     # ADK Runner + InMemorySessionService wrapper
    │   ├── service_app.py                 # FastAPI app with /health and /invoke routes
    │   └── models.py                      # Pydantic request/response models
    ├── news_service/
    │   ├── agent.py                       # SequentialAgent + ParallelAgent pipeline
    │   ├── tools.py                       # Google News RSS fetcher tool
    │   ├── runtime.py                     # ADK Runner wrapper (shared pattern)
    │   ├── service_app.py                 # FastAPI app with /health and /invoke routes
    │   └── models.py                      # Pydantic request/response models
    └── memo_service/
        ├── agent.py                       # SequentialAgent + ParallelAgent + LoopAgent
        ├── runtime.py                     # ADK Runner wrapper (shared pattern)
        ├── service_app.py                 # FastAPI app with /health and /invoke routes
        └── models.py                      # Pydantic request/response models
```

**Design rationale:**

- **Service separation.** Each agent pipeline runs as an independent process. You can restart, scale, or rewrite any service without touching the others.
- **Mirrored front-ends.** `main.py` (CLI) and `streamlit_app.py` (web) follow the exact same pattern: collect inputs → call services → render response. Neither imports any ADK code directly.
- **Shared runtime pattern.** All three services use the same `runtime.py` pattern (`run_agent` / `run_agent_async`) to avoid duplicating ADK boilerplate.
- **Thin FastAPI shell.** `service_app.py` in each service is intentionally minimal — a `/health` check and a single `/invoke` route that delegates straight to `run_agent`.

---

## Step 1 — The Market Data Service (`:8101`)

### The Tool: `render_market_snapshot`

Data fetching lives in `tools.py`. The `render_market_snapshot` tool calls `yfinance`, builds a rich snapshot dictionary — fundamentals, technicals, and price history metrics — and returns it as a JSON string that the LLM can reason over:

```python
def render_market_snapshot(ticker: str) -> str:
    tk = yf.Ticker(ticker)
    info = tk.info or {}
    hist = tk.history(period="1y", interval="1d")
    close = hist["Close"].dropna()
    returns = close.pct_change().dropna()

    snapshot = {
        "ticker": ticker,
        "company_name": info.get("longName") or info.get("shortName") or ticker,
        "sector": info.get("sector"),
        "current_price": float(close.iloc[-1]),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "price_to_book": info.get("priceToBook"),
        "return_on_equity": info.get("returnOnEquity"),
        "debt_to_equity": info.get("debtToEquity"),
        "revenue_growth": info.get("revenueGrowth"),
        "52w_change_pct": round(((close.iloc[-1] / close.iloc[0]) - 1) * 100, 2),
        "daily_volatility_pct": round(float(returns.std() * 100), 2),
        "sma_50": round(float(close.tail(50).mean()), 2),
        "sma_200": round(float(close.tail(200).mean()), 2),
        "price_vs_sma50_pct": round((float(close.iloc[-1]) / float(close.tail(50).mean()) - 1) * 100, 2),
        "price_vs_sma200_pct": round((float(close.iloc[-1]) / float(close.tail(200).mean()) - 1) * 100, 2),
    }
    return json.dumps(snapshot, indent=2, default=str)
```

**Key design decisions:**

- One year of daily price history (`period="1y"`) gives enough data for meaningful 50-day and 200-day moving averages.
- `price_vs_sma50_pct` and `price_vs_sma200_pct` are pre-computed so the LLM receives a ready-to-interpret signal rather than raw prices.
- The function returns JSON (a string), not a Python dict — this is the required return type for ADK tools.

### The Agent Pipeline

The market data service wraps a `SequentialAgent` containing a `ParallelAgent` for concurrent analysis:

```python
def build_root_agent():
    intake_agent = LlmAgent(
        name="ticker_intake",
        model=MODEL,
        instruction="Extract the ticker symbol and restate the request in one concise line.",
        output_key="normalized_request",
    )

    snapshot_agent = LlmAgent(
        name="fundamental_and_technical_analyst",
        model=MODEL,
        tools=[render_market_snapshot],
        instruction=(
            "Use the render_market_snapshot tool to fetch a free market snapshot. "
            "Produce a compact markdown section with key fundamentals and technical context."
        ),
        output_key="market_snapshot_summary",
    )

    interpretation_agent = LlmAgent(
        name="signal_interpreter",
        model=MODEL,
        instruction=(
            "Interpret the market snapshot already available in state. "
            "Discuss valuation, trend posture, volatility, and balance-sheet quality."
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
        instruction="Combine normalized request, market snapshot summary, and market interpretation into one markdown note.",
        output_key="final_market_data_note",
    )

    return SequentialAgent(
        name="market_data_pipeline",
        sub_agents=[intake_agent, parallel_research, final_agent],
    )
```

**How `output_key` works:** When an `LlmAgent` has an `output_key`, ADK automatically writes its final text response into the shared session state under that key. All downstream agents in the same pipeline can then read that value from state — no explicit message passing, no serialisation plumbing required.

**Why `ParallelAgent` here?** The `snapshot_agent` needs to call the `yfinance` tool (I/O bound), while `interpretation_agent` can begin reasoning about whatever data is already in state. Running them concurrently cuts wall-clock time.

---

## Step 2 — The News Service (`:8102`)

### The Tool: `fetch_rss_news`

The news tool is deliberately simple — no paid API, no authentication. It queries the Google News RSS feed for `"{ticker} stock"` and returns the top 8 headlines as a JSON array:

```python
def fetch_rss_news(ticker: str) -> str:
    query = quote(f"{ticker} stock")
    url = f"https://news.google.com/rss/search?q={query}"
    parsed = feedparser.parse(url)
    items = [
        {
            "title": getattr(entry, "title", ""),
            "link": getattr(entry, "link", ""),
            "published": getattr(entry, "published", ""),
            "summary": getattr(entry, "summary", ""),
        }
        for entry in parsed.entries[:8]
    ]
    return json.dumps(items, indent=2)
```

### The Agent Pipeline

The news pipeline mirrors the market data service pattern — `SequentialAgent` with an inner `ParallelAgent` for concurrent specialist analysis:

```python
def build_root_agent():
    fetch_agent = LlmAgent(
        name="news_fetcher",
        model=MODEL,
        tools=[fetch_rss_news],
        instruction="Use the fetch_rss_news tool. Return a concise news digest. Do not invent headlines.",
        output_key="raw_news_digest",
    )

    sentiment_agent = LlmAgent(
        name="news_sentiment_analyst",
        model=MODEL,
        instruction="Analyze the raw news digest in state. Identify 3–5 positives, negatives, and uncertain items.",
        output_key="news_sentiment",
    )

    risk_agent = LlmAgent(
        name="news_risk_analyst",
        model=MODEL,
        instruction="Review the raw news digest in state. Infer potential business, regulatory, or execution risks.",
        output_key="news_risks",
    )

    parallel_agents = ParallelAgent(
        name="parallel_news_review",
        sub_agents=[sentiment_agent, risk_agent],
    )

    synthesis_agent = LlmAgent(
        name="news_synthesis",
        model=MODEL,
        instruction="Combine raw news digest, sentiment view, and risk view into a concise markdown note.",
        output_key="final_news_note",
    )

    return SequentialAgent(
        name="news_pipeline",
        sub_agents=[fetch_agent, parallel_agents, synthesis_agent],
    )
```

The `sentiment_agent` and `risk_agent` run in parallel — both read the `raw_news_digest` from state (written by `fetch_agent`) but produce independent outputs. The `synthesis_agent` then reads all three state keys and merges them.

---

## Step 3 — The Memo Service (`:8103`)

This is the most architecturally interesting service. It uses all three ADK orchestration primitives: `SequentialAgent`, `ParallelAgent`, and `LoopAgent`.

### The Full Pipeline

```python
def build_root_agent():
    # Stage 1 — Intake
    intake_agent = LlmAgent(
        name="memo_intake",
        model=MODEL,
        instruction=(
            "Read the JSON payload. Extract ticker, horizon, risk appetite, "
            "market data note, and news note. Create a clean internal brief."
        ),
        output_key="research_brief",
    )

    # Stage 2 — Parallel specialist analysis
    valuation_agent = LlmAgent(
        name="valuation_specialist", model=MODEL,
        instruction="Using the research brief, explain whether the stock looks cheap, fair, or expensive.",
        output_key="valuation_view",
    )
    momentum_agent = LlmAgent(
        name="momentum_specialist", model=MODEL,
        instruction="Using the research brief, explain what price trend and volatility imply for the selected horizon.",
        output_key="momentum_view",
    )
    risk_agent = LlmAgent(
        name="risk_specialist", model=MODEL,
        instruction="Using the research brief, identify the most important downside risks and uncertainties.",
        output_key="risk_view",
    )
    parallel_stage = ParallelAgent(
        name="parallel_specialist_stage",
        sub_agents=[valuation_agent, momentum_agent, risk_agent],
    )

    # Stage 3 — First-draft memo
    writer_agent = LlmAgent(
        name="memo_writer",
        model=MODEL,
        instruction=(
            "Write a business-friendly markdown investment memo with these sections: "
            "Company snapshot, Bull case, Bear case, What the market data says, "
            "What the news says, Decision stance, and What would change my mind. "
            "End with one of: Watchlist / Hold / Accumulate / Avoid."
        ),
        output_key="draft_memo",
    )

    # Stage 4 — LoopAgent: iterative refinement (critic → rewriter, 2 iterations)
    critic_agent = LlmAgent(
        name="memo_critic", model=MODEL,
        instruction=(
            "Critique the draft memo in state. Check clarity, internal consistency, "
            "unsupported claims, and whether the recommendation matches the evidence."
        ),
        output_key="memo_critique",
    )
    rewriter_agent = LlmAgent(
        name="memo_rewriter", model=MODEL,
        instruction=(
            "Rewrite the memo using the critique in state. Improve structure, "
            "reduce overclaiming, and tighten the final recommendation."
        ),
        output_key="draft_memo",       # ← overwrites the draft in-place each iteration
    )
    refinement_loop = LoopAgent(
        name="memo_refinement_loop",
        sub_agents=[critic_agent, rewriter_agent],
        max_iterations=2,
    )

    # Stage 5 — Finalizer
    finalizer = LlmAgent(
        name="finalizer", model=MODEL,
        instruction="Return the final markdown memo from state. Preserve headings and make it readable.",
        output_key="final_memo",
    )

    return SequentialAgent(
        name="memo_pipeline",
        sub_agents=[intake_agent, parallel_stage, writer_agent, refinement_loop, finalizer],
    )
```

**Why the `LoopAgent` matters:**

The `critic_agent` and `rewriter_agent` run in a 2-iteration loop. After the first draft is written, the critic reads it and produces actionable rewrite guidance. The rewriter then produces a new `draft_memo` (overwriting the old one via the same `output_key`). After `max_iterations=2` full critic/rewriter cycles, the finalizer emits the polished memo. This mirrors how a human analyst would self-review before publishing.

**Parallel specialist stage:** The three specialist agents — valuation, momentum, and risk — are completely independent and can run concurrently. Each reads the `research_brief` from state and writes its own output key. The `writer_agent` then reads all three when composing the first draft.

---

## Step 4 — The Shared FastAPI Shell

Every service exposes the same two HTTP routes via the same FastAPI pattern. Here is the market data service's `service_app.py` as a representative example:

```python
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
    prompt = req.prompt or "Analyze this JSON payload:\n\n" + str(req.payload)
    result = run_agent(agent=agent, prompt=prompt, initial_state={"input_payload": req.payload})
    return AgentResponse(result=result, meta={"service": "market_data_service"})
```

`build_root_agent()` is called on every request — ADK agents are stateless by design, so this is safe and avoids any cross-request state leakage.

---

## Step 5 — The Shared ADK Runtime

Each service has an identical `runtime.py` that wraps ADK's `Runner` and `InMemorySessionService`. This is the glue between FastAPI and the ADK agent:

```python
async def run_agent_async(agent, prompt, initial_state=None) -> str:
    app_name = os.getenv("APP_NAME", "local_adk_app")
    user_id  = os.getenv("ADK_USER_ID", "demo_user")

    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)

    session = await runner.session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state or {},
        session_id=str(uuid.uuid4()),     # Fresh session per request
    )

    user_message = types.Content(role="user", parts=[types.Part(text=prompt)])

    final_text = ""
    async for event in runner.run_async(
        user_id=user_id, session_id=session.id, new_message=user_message
    ):
        text = flatten_text_from_event(event)
        if text:
            final_text = text

    await runner.close()
    return final_text

def run_agent(agent, prompt, initial_state=None) -> str:
    return asyncio.run(run_agent_async(agent=agent, prompt=prompt, initial_state=initial_state))
```

**Key design choices:**

- A new `uuid4()` session ID is generated per request, ensuring complete isolation between concurrent calls.
- `initial_state` injects the HTTP payload directly into session state — that's what makes `{ticker}`, `{market_data}`, etc. available to agent prompt templates automatically.
- The `flatten_text_from_event` helper extracts the last meaningful text from the stream so we always capture the final agent output.
- `runner.close()` is always called in a `finally` block to avoid resource leaks.

---

## Step 6 — The Front-Ends

### CLI (`main.py`)

```python
MARKET_DATA_URL = "http://127.0.0.1:8101/invoke"
NEWS_URL        = "http://127.0.0.1:8102/invoke"
MEMO_URL        = "http://127.0.0.1:8103/invoke"

def main() -> None:
    ticker  = input("Enter ticker (example: MSFT or TCS.NS): ").strip()
    horizon = input("Investment horizon (example: 3 years): ").strip() or "3 years"
    risk    = input("Risk appetite (low/medium/high): ").strip() or "medium"

    market_resp = requests.post(MARKET_DATA_URL, json={"payload": {"ticker": ticker}})
    news_resp   = requests.post(NEWS_URL,         json={"payload": {"ticker": ticker}})

    combined_payload = {
        "ticker":              ticker,
        "horizon":             horizon,
        "risk_appetite":       risk,
        "market_data_analysis": market_resp.json()["result"],
        "news_analysis":        news_resp.json()["result"],
    }

    memo_resp = requests.post(MEMO_URL, json={"payload": combined_payload})
    Console().print("\n" + memo_resp.json()["result"])
```

### Streamlit Web UI (`streamlit_app.py`)

```python
st.set_page_config(page_title="Investment Research Copilot", layout="wide")
st.title("Retail Investment Research Copilot")

ticker  = st.text_input("Ticker", value="MSFT")
horizon = st.selectbox("Horizon", ["6 months", "1 year", "3 years", "5 years"], index=2)
risk    = st.selectbox("Risk appetite", ["low", "medium", "high"], index=1)

if st.button("Generate memo"):
    with st.spinner("Calling local services..."):
        market_resp = requests.post("http://127.0.0.1:8101/invoke", json={"payload": {"ticker": ticker}})
        news_resp   = requests.post("http://127.0.0.1:8102/invoke", json={"payload": {"ticker": ticker}})

        memo_payload = {
            "ticker": ticker, "horizon": horizon, "risk_appetite": risk,
            "market_data": market_resp.json()["result"],
            "news_analysis": news_resp.json()["result"],
        }
        memo_resp = requests.post("http://127.0.0.1:8103/invoke", json={"payload": memo_payload})

    st.markdown(memo_resp.json()["result"])
```

Neither front-end imports any ADK code. They are plain synchronous HTTP clients — no `asyncio`, no `nest_asyncio`, no session management. The architectural separation is clean.

---

## Setup & Installation

### Prerequisites

- Python ≥ 3.11
- [**uv**](https://docs.astral.sh/uv/) — fast Python package and environment manager
- An Anthropic API key (`ANTHROPIC_API_KEY`)

### 1. Clone the repository

```bash
git clone <repo-url>
cd learning_google_adk/projects/retail_investment_research_copilot
```

### 2. Create and activate a virtual environment

```bash
uv venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Configure API keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

### Key Dependencies

| Package | Purpose |
|---------|---------|
| `google-adk` | Google Agent Development Kit — SequentialAgent, ParallelAgent, LoopAgent, LlmAgent, Runner |
| `litellm` | Unified LLM API gateway (routes calls to Anthropic, OpenAI, Google, etc.) |
| `yfinance` | Free real-time stock data from Yahoo Finance |
| `feedparser` | Parses Google News RSS feeds |
| `fastapi` | HTTP framework powering each agent service |
| `uvicorn` | ASGI server that runs the FastAPI services |
| `requests` | HTTP client used by `main.py` and `streamlit_app.py` |
| `streamlit` | Web UI framework for the browser front-end |
| `python-dotenv` | Loads API keys from `.env` at runtime |
| `pydantic` | Request/response model validation |
| `rich` | Beautiful terminal output (Markdown rendering) |

---

## Running the Application

Running the application is a **two-step process**: first start all three agent services, then run your chosen front-end.

### Step 1 — Start All Services

From the project root, run:

```bash
python scripts/start_services.py
```

This launches all three FastAPI/Uvicorn services simultaneously:

| Service | Module | Port |
|---|---|---|
| Market Data Service | `agents.market_data_service.service_app` | `:8101` |
| News Service | `agents.news_service.service_app` | `:8102` |
| Memo Service | `agents.memo_service.service_app` | `:8103` |

You should see output like:

```
Starting market-data-service on port 8101...
Starting news-service on port 8102...
Starting memo-service on port 8103...
```

Keep this terminal open. Press **Ctrl+C** when you want to stop all services.

> **Alternative:** You can start each service manually in a separate terminal if you prefer:
> ```bash
> uvicorn agents.market_data_service.service_app:app --host 127.0.0.1 --port 8101 --reload
> uvicorn agents.news_service.service_app:app         --host 127.0.0.1 --port 8102 --reload
> uvicorn agents.memo_service.service_app:app         --host 127.0.0.1 --port 8103 --reload
> ```

### Step 2a — CLI Mode

In a second terminal:

```bash
python main.py
```

You'll be prompted for three inputs:

```
Enter ticker (example: MSFT or TCS.NS): AAPL
Investment horizon (example: 3 years): 3 years
Risk appetite (low/medium/high): medium
```

The application calls all three services in sequence, then renders the investment memo directly in the terminal using `rich`.

### Step 2b — Streamlit Web UI

In a second terminal:

```bash
streamlit run streamlit_app.py
```

This opens the browser UI at `http://localhost:8501`. Enter the ticker, choose a horizon and risk appetite from the dropdowns, click **Generate memo**, and the rendered Markdown memo will appear on the page.

---

## Sample Output

*(Screenshot to be inserted here)*

---

## Conclusion

We've built a fully functional, service-oriented investment research copilot that:

- Pulls live market data (fundamentals + technicals) from Yahoo Finance,
- Scrapes and analyses recent news from Google News RSS,
- Synthesises both into a structured investment memo via three specialist LLM agents,
- Iteratively refines the memo through an automated critic → rewriter loop.

**What makes this architecture interesting:**

- **True microservice separation.** Each ADK pipeline runs as its own FastAPI/Uvicorn process. You can restart, upgrade, or swap any service independently without touching the others — or the front-ends.
- **Composing ADK primitives deliberately.** `SequentialAgent` for deterministic control flow, `ParallelAgent` for concurrent specialists, `LoopAgent` for quality refinement. Each primitive is used where it earns its keep.
- **State as a shared blackboard.** `output_key` on every `LlmAgent` writes results to session state. No explicit message passing, no serialisation boilerplate — downstream agents simply read what upstream agents wrote.
- **Model-agnostic via LiteLlm.** Swapping from Claude to GPT-4o or Gemini is a single line change: `LiteLlm(model="openai/gpt-4o")`.
- **Front-ends are just HTTP clients.** Neither `main.py` nor `streamlit_app.py` imports a single line of ADK. They POST a payload, receive a Markdown string, and render it. The separation of concerns is clean and production-grade.

---

*If you enjoyed this post, follow me for more on agentic AI, multi-service architectures, and building practical AI-powered tools with Google ADK.*
