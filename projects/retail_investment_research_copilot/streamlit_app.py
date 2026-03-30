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
