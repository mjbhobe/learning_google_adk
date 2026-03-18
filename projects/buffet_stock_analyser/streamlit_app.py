import streamlit as st
import asyncio
from dotenv import load_dotenv

from google.adk.sessions import InMemorySessionService

from logger import get_logger
from buffet_bot.agent import root_agent as workflow
from utils import get_stock_info, run_agent_query

load_dotenv(override=True)
logger = get_logger("buffet_stock_analyser.streamlit_app")

st.set_page_config(page_title="Buffett AI", page_icon="💰")

st.title("💰 Buffett-Bot: Agentic Value Analyst")
st.markdown("Powered by **Google ADK 2026** and **Claude 4.6 Sonnet**.")

ticker = st.text_input("Enter Ticker Symbol", value="AAPL").upper()

if st.button("Analyze Stock"):
    with st.status("Agents are working...", expanded=True) as status:
        # We manually trigger the runner here to capture output for Streamlit
        from google.adk.agents import SequentialAgent
        from google.adk.runtime import Runner
        from agents.collector.collector import DataCollectorAgent
        from agents.analyst.analyst import BuffettAnalystAgent
        from agents.reporter.reporter import MarkdownReporterAgent

        workflow = SequentialAgent(
            name="UI_Workflow",
            sub_agents=[
                DataCollectorAgent(),
                BuffettAnalystAgent(),
                MarkdownReporterAgent(),
            ],
        )

        runner = Runner(agent=workflow)
        session = runner.create_session(state={"symbol": ticker})

        async def run_ui():
            async for event in runner.run(session):
                st.write(
                    f"**{event.agent_name}**: {event.message if hasattr(event, 'message') else 'Processing...'}"
                )

        asyncio.run(run_ui())
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    st.markdown("---")
    st.markdown(session.state.get("final_markdown_report"))
