import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv(override=True)
if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("FATAL: `ANTHROPIC_API_KEY` not found in `.env` file!")
    st.stop()

st.set_page_config(page_title="Buffett AI", page_icon="💰")
st.title("💰 Buffett-Bot: Agentic Value Analyst")
st.markdown("Powered by **Google ADK** and **Claude 4.6 Sonnet**.")

symbol = st.text_input("Enter Ticker Symbol", value="AAPL").strip().upper()


@st.cache_resource
def _init_pipeline():
    """One-time heavy initialisation (cached across Streamlit reruns).

    Imports google-adk, litellm, yfinance and builds the agent pipeline.
    Everything expensive is inside this function so the Streamlit server
    starts instantly.
    """
    import nest_asyncio

    nest_asyncio.apply()

    from google.adk.sessions import InMemorySessionService
    from buffet_bot.agent import root_agent

    return root_agent, InMemorySessionService()


if st.button("Analyze Stock"):
    from pathlib import Path
    import asyncio
    import uuid

    from utils import get_stock_info, run_agent_query

    with st.status("Initialising agents (first run only)…", expanded=True) as status:
        workflow, session_service = _init_pipeline()
        status.update(label=f"📡 Fetching live data for **{symbol}**…")

        app_name = Path(__file__).parent.resolve().name
        user_id = "buffet_analyst_007"
        session_id = str(uuid.uuid4())

        company_info, raw_financials = get_stock_info(symbol)

        status.update(label="🤖 Running Buffett analysis pipeline…")

        async def _run_analysis():
            my_session = await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state={
                    "symbol": symbol,
                    "company_info": company_info,
                    "raw_financials": raw_financials,
                },
            )
            return await run_agent_query(
                agent=workflow,
                session_service=session_service,
                app_name=app_name,
                user_id=user_id,
                user_query=f"Analyse the stock {symbol}",
                session=my_session,
            )

        loop = asyncio.get_event_loop()
        final_report = loop.run_until_complete(_run_analysis())
        status.update(label="✅ Analysis complete!", state="complete", expanded=False)

    st.markdown("---")
    if final_report:
        st.markdown(final_report)
    else:
        st.error("No report was generated. The agent did not return a final response.")
