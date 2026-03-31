import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

MARKET_DATA_URL = os.getenv("MARKET_DATA_SERVICE_URL", "http://127.0.0.1:8101/invoke")
NEWS_URL = os.getenv("NEWS_SERVICE_URL", "http://127.0.0.1:8102/invoke")
MEMO_URL = os.getenv("MEMO_SERVICE_URL", "http://127.0.0.1:8103/invoke")

st.set_page_config(page_title="Investment Research Copilot", layout="wide")
st.title("📊 Retail Investment Research Copilot")

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Ticker", value="MSFT")
with col2:
    horizon = st.selectbox(
        "Horizon", ["6 months", "1 year", "3 years", "5 years"], index=2
    )
with col3:
    risk = st.selectbox("Risk appetite", ["low", "medium", "high"], index=1)

if st.button("Generate memo"):
    with st.status("Orchestrating AI agents...", expanded=True) as status:
        st.write("📊 Calling Market Data Service...")
        market_resp = requests.post(
            MARKET_DATA_URL, json={"payload": {"ticker": ticker}}
        )
        market_resp.raise_for_status()

        st.write("📰 Calling News Service...")
        news_resp = requests.post(NEWS_URL, json={"payload": {"ticker": ticker}})
        news_resp.raise_for_status()

        st.write("🧠 Compiling analyses for Memo Service...")
        memo_payload = {
            "ticker": ticker,
            "horizon": horizon,
            "risk_appetite": risk,
            "market_data_analysis": market_resp.json()["result"],
            "news_analysis": news_resp.json()["result"],
        }

        st.write("✍️ Generating and refining final investment memo...")
        memo_resp = requests.post(MEMO_URL, json={"payload": memo_payload})
        memo_resp.raise_for_status()

        status.update(label="👍 Research complete!", state="complete", expanded=False)

    tab1, tab2, tab3 = st.tabs(["Final Memo", "Market Data", "News Analysis"])

    with tab1:
        st.markdown(memo_resp.json()["result"])

    with tab2:
        st.markdown(market_resp.json()["result"])

    with tab3:
        st.markdown(news_resp.json()["result"])
