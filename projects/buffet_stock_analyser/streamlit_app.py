import streamlit as st
import asyncio
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

import nest_asyncio

from google.adk.sessions import InMemorySessionService

from logger import get_logger
from buffet_bot.agent import root_agent as workflow
from utils import get_stock_info, run_agent_query

# Streamlit internally uses asyncio. Calling asyncio.run() from
# within a Streamlit app can raise a `RuntimeError: This event loop is
# already running` because Streamlit already has an event loop.
# A reliable fix is to use the nest_asyncio package & use nest_asyncio.apply()
nest_asyncio.apply()

load_dotenv(override=True)
assert os.getenv(
    "ANTHROPIC_API_KEY"
), "FATAL ERROR: ANTHROPIC_API_KEY not found in .env file!"
logger = get_logger("buffet_stock_analyser.streamlit_app")

app_name = Path(__file__).parent.resolve().name
user_id = "buffet_analyst_007"

# Create a session_service instance
session_service = InMemorySessionService()

st.set_page_config(page_title="Buffett AI", page_icon="💰")

st.title("💰 Buffett-Bot: Agentic Value Analyst")
st.markdown("Powered by **Google ADK 2026** and **Claude 4.6 Sonnet**.")

symbol = st.text_input("Enter Ticker Symbol", value="AAPL").strip().upper()

if st.button("Analyze Stock"):
    # Generate a new session_id per analysis run
    session_id = str(uuid.uuid4())

    with st.status("Agents are working...", expanded=True) as status:

        async def run_ui():
            company_info, raw_financials = get_stock_info(symbol)
            initial_state = {
                "symbol": symbol,
                "company_info": company_info,
                "raw_financials": raw_financials,
            }

            my_session = await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state=initial_state,
            )
            logger.info(f"\n Created session with initial_state = {initial_state}\n")

            final_markdown_report = await run_agent_query(
                agent=workflow,
                session_service=session_service,
                app_name=app_name,
                user_id=user_id,
                user_query=f"Analyse the stock {symbol}",
                session=my_session,
            )

            return final_markdown_report

        final_markdown_report = asyncio.run(run_ui())
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    st.markdown("---")
    if final_markdown_report:
        st.markdown(final_markdown_report)
    else:
        st.error("No report was generated. The agent did not return a final response.")
