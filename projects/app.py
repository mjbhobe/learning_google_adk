import streamlit as st

from stock_analysis_adk.orchestrator import run_full_analysis

st.set_page_config(
    page_title="ADK Stock Analysis",
    page_icon="📈",
    layout="wide",
)

if "report" not in st.session_state:
    st.session_state.report = ""
if "run_meta" not in st.session_state:
    st.session_state.run_meta = {}

st.markdown(
    '''
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 1rem;}
    .metric-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white; padding: 18px; border-radius: 16px; box-shadow: 0 10px 30px rgba(2,6,23,.20);
        border: 1px solid rgba(255,255,255,.08);
    }
    .hero {
        padding: 18px 22px; border-radius: 18px; background: linear-gradient(135deg,#eff6ff 0%,#ecfeff 100%);
        border: 1px solid #dbeafe; margin-bottom: 16px;
    }
    </style>
    ''',
    unsafe_allow_html=True,
)

st.markdown(
    '''
    <div class="hero">
        <h2 style="margin-bottom:0.25rem;">ADK + Claude Sonnet Stock Analysis</h2>
        <div style="color:#334155;">
            Deterministic Python data pipeline for downloads and calculations, with ADK agents used only for interpretation and recommendation.
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1642543492481-44e81e3914a7?auto=format&fit=crop&w=1200&q=80")
    st.header("Run analysis")
    symbol = st.text_input("Ticker", value="AAPL").upper().strip()
    run_clicked = st.button("Generate report", type="primary", use_container_width=True)
    st.caption("Best results for liquid public equities. U.S. tickers get the richest filing support.")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><h4>Analysis modules</h4><div>Business fundamentals, financial ratios, peer benchmarking, sentiment, final recommendation.</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h4>Token discipline</h4><div>All downloads and calculations happen in Python. Only compact evidence packs go to the LLM.</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h4>Output</h4><div>Structured Markdown report suitable for review, export, or further editing.</div></div>', unsafe_allow_html=True)

if run_clicked and symbol:
    progress = st.progress(0, text="Starting analysis…")
    status = st.empty()

    status.info("Downloading market data and statements…")
    progress.progress(15)

    status.info("Computing raw metrics and evidence packs…")
    progress.progress(35)

    status.info("Running ADK sub-agents in parallel…")
    progress.progress(65)

    result = run_full_analysis(symbol)
    st.session_state.report = result["report_markdown"]
    st.session_state.run_meta = result["summary"]

    status.success("Analysis complete.")
    progress.progress(100)

if st.session_state.report:
    meta = st.session_state.run_meta
    top = st.columns(4)
    top[0].metric("Symbol", meta.get("symbol", "-"))
    top[1].metric("Peers used", meta.get("peer_count", 0))
    top[2].metric("News items", meta.get("news_count", 0))
    top[3].metric("Recommendation", meta.get("recommendation", "N/A"))

    st.markdown("---")
    st.markdown(st.session_state.report)
