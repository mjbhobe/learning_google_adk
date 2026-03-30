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
       │   + LoopAgent refinement)   │     → writer → loop(critic,rewriter)]
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
    ├── common/
    │   ├── __init__.py
    │   ├── runtime.py                     # Shared ADK Runner wrapper
    │   └── models.py                      # Shared Pydantic request/response models
    ├── market_data_service/
    │   ├── agent.py                       # SequentialAgent + ParallelAgent pipeline
    │   ├── tools.py                       # yfinance data fetching tool
    │   ├── runtime.py                     # Per-service runtime (re-exports common)
    │   ├── service_app.py                 # FastAPI app with /health and /invoke routes
    │   └── models.py                      # Per-service models (re-exports common)
    ├── news_service/
    │   ├── agent.py                       # SequentialAgent + ParallelAgent pipeline
    │   ├── tools.py                       # Google News RSS fetcher tool
    │   ├── runtime.py                     # Per-service runtime (re-exports common)
    │   ├── service_app.py                 # FastAPI app with /health and /invoke routes
    │   └── models.py                      # Per-service models (re-exports common)
    └── memo_service/
        ├── agent.py                       # SequentialAgent + ParallelAgent + LoopAgent
        ├── runtime.py                     # Per-service runtime (re-exports common)
        ├── service_app.py                 # FastAPI app with /health and /invoke routes
        └── models.py                      # Per-service models (re-exports common)
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
def get_market_snapshot(ticker: str) -> Dict[str, Any]:
    logger.info(f"In market_data_service::get_market_snapshot() -> {ticker}")
    tk = yf.Ticker(ticker)
    info = tk.info or {}
    hist = tk.history(period="1y", interval="1d")

    if hist.empty:
        ret_val = {"ticker": ticker, "error": "No market data returned by yfinance."}
        logger.info(f"Exiting market_data_service::get_market_snapshot() -> {ret_val}")
        return ret_val

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
        "daily_volatility_pct": round(float(returns.std() * 100), 2)
        if not returns.empty
        else None,
        "avg_volume": int(hist["Volume"].tail(60).mean())
        if "Volume" in hist.columns
        else None,
        "sma_50": round(float(close.tail(50).mean()), 2),
        "sma_200": round(float(close.tail(200).mean()), 2),
        "price_vs_sma50_pct": round(
            (float(close.iloc[-1]) / float(close.tail(50).mean()) - 1) * 100, 2
        ),
        "price_vs_sma200_pct": round(
            (float(close.iloc[-1]) / float(close.tail(200).mean()) - 1) * 100, 2
        ),
    }
    logger.info(f"market_data_service::get_market_snapshot(): snapshot -> {snapshot}")
    return snapshot

def render_market_snapshot(ticker: str) -> str:
    snapshot = get_market_snapshot(ticker)
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
    logger.info("In market_data_service::build_root_agent()")

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
            "Use the render_market_snapshot tool to fetch market data for the ticker in: {normalized_request}\n"
            "Produce a compact markdown section covering key fundamentals (PE, PB, ROE, D/E, dividend yield, "
            "revenue/earnings growth) and technical context (price vs SMA50/SMA200, 52-week change, "
            "daily volatility). Be factual. Note any missing or unreliable data explicitly."
        ),
        output_key="market_snapshot_summary",
    )

    interpretation_agent = LlmAgent(
        name="signal_interpreter",
        model=MODEL,
        instruction=(
            "Use the market snapshot below to write a plain-language interpretation.\n\n"
            "{market_snapshot_summary}\n\n"
            "Cover: valuation posture (cheap/fair/expensive), price trend (bullish/bearish/sideways), "
            "volatility level, and balance-sheet quality. Maximum 200 words."
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
            "Combine the inputs below into one concise markdown note for the downstream memo service.\n\n"
            "## Request\n{normalized_request}\n\n"
            "## Market Snapshot\n{market_snapshot_summary}\n\n"
            "## Signal Interpretation\n{market_interpretation}\n\n"
            "Preserve all numbers. Do not add commentary beyond what is already present."
        ),
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
```

### The Agent Pipeline

The news pipeline mirrors the market data service pattern — `SequentialAgent` with an inner `ParallelAgent` for concurrent specialist analysis:

```python
def build_root_agent():
    logger.info("In news_service::build_root_agent() ->")
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
            "Analyse the news digest below.\n\n"
            "{raw_news_digest}\n\n"
            "Identify 3–5 positives, 3–5 negatives, and up to 3 uncertain/ambiguous items "
            "that could affect the company's outlook. Use bullet points per category."
        ),
        output_key="news_sentiment",
    )

    risk_agent = LlmAgent(
        name="news_risk_analyst",
        model=MODEL,
        instruction=(
            "Review the news digest below.\n\n"
            "{raw_news_digest}\n\n"
            "Infer potential business, regulatory, or execution risks. "
            "Stay conservative — only flag risks with at least weak evidence in the digest. "
            "Maximum 5 bullet points."
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
            "Combine the inputs below into a concise markdown note for a downstream investment memo.\n\n"
            "## News Digest\n{raw_news_digest}\n\n"
            "## Sentiment Analysis\n{news_sentiment}\n\n"
            "## Risk Flags\n{news_risks}\n\n"
            "Write a summary section (3–4 sentences) followed by labelled Positives, Negatives, "
            "and Risk subsections. Keep it under 300 words total."
        ),
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
    logger.info("In memo_service::build_root_agent() ->")

    # ------------------------------------------------------------------
    # Stage 1 — Intake
    # Parses the raw JSON payload and produces a clean prose brief that
    # all downstream agents can read without having to re-parse JSON.
    # ------------------------------------------------------------------
    intake_agent = LlmAgent(
        name="memo_intake",
        model=MODEL,
        instruction=(
            "You will receive a JSON payload containing the following fields: "
            "ticker, horizon, risk_appetite, market_data_analysis (or market_data), and news_analysis. "
            "Extract all fields and write a concise internal research brief in plain prose. "
            "Label each section clearly: Ticker, Horizon, Risk Appetite, Market Data Summary, News Summary. "
            "Do not add opinions — just organise the facts."
        ),
        output_key="research_brief",
    )

    # ------------------------------------------------------------------
    # Stage 2 — Parallel specialist analysis
    # Each agent receives the research_brief directly via {research_brief}
    # interpolation, so ADK injects the exact text with no ambiguity.
    # ------------------------------------------------------------------
    valuation_agent = LlmAgent(
        name="valuation_specialist",
        model=MODEL,
        instruction=(
            "You are a valuation analyst. Use the research brief below.\n\n"
            "{research_brief}\n\n"
            "In 150 words or fewer, state whether the stock looks cheap, fair, or expensive. "
            "Cite only ratios already present in the brief. Do not fabricate numbers."
        ),
        output_key="valuation_view",
    )

    momentum_agent = LlmAgent(
        name="momentum_specialist",
        model=MODEL,
        instruction=(
            "You are a technical/momentum analyst. Use the research brief below.\n\n"
            "{research_brief}\n\n"
            "In 150 words or fewer, explain what the price trend and volatility data imply "
            "for the investment horizon stated in the brief."
        ),
        output_key="momentum_view",
    )

    risk_agent = LlmAgent(
        name="risk_specialist",
        model=MODEL,
        instruction=(
            "You are a risk analyst. Use the research brief below.\n\n"
            "{research_brief}\n\n"
            "In 150 words or fewer, identify the three most important downside risks. "
            "Stay conservative — do not speculate beyond what the brief contains."
        ),
        output_key="risk_view",
    )

    parallel_stage = ParallelAgent(
        name="parallel_specialist_stage",
        sub_agents=[valuation_agent, momentum_agent, risk_agent],
    )

    # ------------------------------------------------------------------
    # Stage 3 — First-draft memo
    # Writer receives all four keys directly, removing any need for the
    # model to search through full session state.
    # ------------------------------------------------------------------
    writer_agent = LlmAgent(
        name="memo_writer",
        model=MODEL,
        instruction=(
            "You are a senior investment analyst writing an educational memo. "
            "Use the inputs below — do not invent data not present in them.\n\n"
            "## Research Brief\n{research_brief}\n\n"
            "## Valuation View\n{valuation_view}\n\n"
            "## Momentum View\n{momentum_view}\n\n"
            "## Risk View\n{risk_view}\n\n"
            "Write a concise markdown investment memo with these sections:\n"
            "1. Company Snapshot\n"
            "2. Bull Case\n"
            "3. Bear Case\n"
            "4. What the Market Data Says\n"
            "5. What the News Says\n"
            "6. Decision Stance (end with exactly one of: Watchlist / Hold / Accumulate / Avoid)\n"
            "7. What Would Change My Mind\n\n"
            "Keep each section to 3–5 sentences. "
            "Add a footer: *This memo is for educational purposes only and is not investment advice.*"
        ),
        output_key="draft_memo",
    )

    # ------------------------------------------------------------------
    # Stage 4 — Single refinement pass (critic → rewriter)
    # max_iterations=1 means one critic call + one rewriter call (2 LLM
    # round-trips) vs the previous 2 iterations (4 round-trips).
    # The rewriter's output IS the final memo — no separate finalizer needed.
    # ------------------------------------------------------------------
    critic_agent = LlmAgent(
        name="memo_critic",
        model=MODEL,
        instruction=(
            "Review the draft memo below.\n\n"
            "{draft_memo}\n\n"
            "Check for: unsupported claims, internal inconsistencies, unclear language, "
            "and whether the Decision Stance matches the evidence. "
            "Produce a numbered list of specific, actionable rewrite instructions. "
            "Be concise — maximum 5 items."
        ),
        output_key="memo_critique",
    )

    rewriter_agent = LlmAgent(
        name="memo_rewriter",
        model=MODEL,
        instruction=(
            "Rewrite the memo below using the critique as a guide.\n\n"
            "## Draft Memo\n{draft_memo}\n\n"
            "## Critique\n{memo_critique}\n\n"
            "Apply every critique point. Keep the same section structure. "
            "Do not add new data not present in the draft. "
            "Return only the final markdown memo — no preamble."
        ),
        output_key="draft_memo",   # overwrites in-place; becomes the final output
    )

    refinement_loop = LoopAgent(
        name="memo_refinement_loop",
        sub_agents=[critic_agent, rewriter_agent],
        max_iterations=1,          # was 2 — saves 2 full LLM round-trips
    )

    return SequentialAgent(
        name="memo_pipeline",
        sub_agents=[
            intake_agent,       # 1 LLM call
            parallel_stage,     # 3 LLM calls (concurrent)
            writer_agent,       # 1 LLM call
            refinement_loop,    # 2 LLM calls (critic + rewriter)
            # Total: 7 LLM calls, 3 of which run in parallel
            # (was 9 calls with max_iterations=2 + finalizer)
        ],
    )
```

**Why the `LoopAgent` matters:**

The `critic_agent` and `rewriter_agent` run in a 1-iteration loop. After the first draft is written, the critic reads it and produces actionable rewrite guidance. The rewriter then produces a new `draft_memo` (overwriting the old one via the same `output_key`). With `max_iterations=1`, this single critic/rewriter cycle completes the process, and the rewriter's output acts as the final polished memo. This mirrors how a human analyst would self-review before publishing.

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
    if req.prompt:
        prompt = req.prompt
    else:
        prompt = "Analyze this JSON payload and produce the required result:\n\n" + str(req.payload)
    result = run_agent(agent=agent, prompt=prompt, initial_state={"input_payload": req.payload})
    return AgentResponse(result=result, meta={"service": "market_data_service"})
```

`build_root_agent()` is called on every request — ADK agents are stateless by design, so this is safe and avoids any cross-request state leakage.

---

## Step 5 — The Shared ADK Runtime

There is a shared `agents.common.runtime` module that configures ADK's `Runner` and `InMemorySessionService`. Each service simply re-exports this logic to avoid duplicated boilerplate:

```python
async def run_agent_async(
    agent: Any,
    prompt: str,
    initial_state: Optional[Dict[str, Any]] = None,
) -> str:
    """Run an ADK agent in-process and return the final text response."""
    app_name = os.getenv("APP_NAME", "local_adk_app")
    user_id = os.getenv("ADK_USER_ID", "demo_user")

    logger.info(f"run_agent_async: app_name={app_name!r}, agent={agent.name!r}")

    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)

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

    logger.info(f"run_agent_async: agent={agent.name!r} finished, response length={len(final_text)}")
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
