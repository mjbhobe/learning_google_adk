import streamlit as st
import os
import requests
from dotenv import load_dotenv

from utils import is_valid_stock_symbol, get_stock_info

load_dotenv(override=True)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Buffett AI", page_icon="💰",layout="wide")
st.title("💰 Buffett-Bot: Agentic Value Analyst")
st.markdown("Powered by **Google ADK**, **Claude 4.6 Sonnet** and a **FastAPI** agent service.")

# ── Server URL (mirrors main.py HOST_AGENT_URL) ───────────────────────────────
HOST_AGENT_URL = os.getenv("HOST_AGENT_URL", "http://localhost:8000/run")

# ── Input ─────────────────────────────────────────────────────────────────────
symbol = st.text_input("Enter Ticker Symbol", value="AAPL").strip().upper()

if st.button("Analyze Stock"):
    if not is_valid_stock_symbol(symbol):
        st.error(f"🚨 Invalid stock symbol: {symbol}. Please try again.")
        st.stop()

    with st.status(f"📡 Fetching live data for **{symbol}**…", expanded=True) as status:

        # Step 1 — pull financial data (same as main.py)
        try:
            company_info, raw_financials = get_stock_info(symbol)
        except Exception as ex:
            st.error(f"Failed to fetch data for **{symbol}**: {ex}")
            st.stop()

        payload = {
            "symbol": symbol,
            "company_info": company_info,
            "raw_financials": raw_financials,
        }

        # Step 2 — call the FastAPI agent service (same as main.py)
        status.update(label="🤖 Running Buffett analysis pipeline…")
        try:
            response = requests.post(HOST_AGENT_URL, json=payload, timeout=120)
        except requests.exceptions.ConnectionError:
            st.error(
                f"Could not connect to the agent server at `{HOST_AGENT_URL}`. "
                "Make sure you have started the server with `./servers.sh` (or "
                "`uvicorn buffet_bot.agents.__main__:app --port 8000`) before "
                "running the Streamlit app."
            )
            st.stop()

        # Step 3 — render result
        if response.ok:
            data = response.json().get("formatted_report", {})
            analysis_report = data.get("analysis_report") if isinstance(data, dict) else None
            status.update(label="✅ Analysis complete!", state="complete", expanded=False)
        else:
            status.update(label="❌ Agent request failed.", state="error", expanded=False)
            st.error(
                f"Agent returned HTTP {response.status_code}. "
                "Check the server logs for details."
            )
            st.stop()

    st.markdown("---")
    if analysis_report:
        st.markdown(analysis_report)
    else:
        st.error("No report was returned by the agent. Check the server logs.")
