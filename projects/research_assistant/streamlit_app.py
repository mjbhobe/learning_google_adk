"""
streamlit_app.py - Streamlit frontend for the Research Assistant
(Marketing Campaign Brief Generator)
"""

import asyncio
from dotenv import load_dotenv
import streamlit as st
from io import StringIO

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# --- Import agents and utilities from the existing code ---
# These imports work because streamlit_app.py is in the same directory
from agent import root_agent
from utils import load_agent_config

load_dotenv(override=True)


# ──────────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🚀 Marketing Campaign Brief Generator",
    page_icon="🚀",
    layout="wide",
)


# ──────────────────────────────────────────────────────────
# Custom CSS for a polished look
# ──────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }

    /* Final output card */
    .final-output {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
    }

    /* Agent trace styling */
    .agent-event {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        padding: 0.3rem 0;
        border-bottom: 1px solid #eee;
    }
    .agent-name {
        color: #667eea;
        font-weight: bold;
    }

    /* Status indicator */
    .status-running {
        color: #f59e0b;
        font-weight: bold;
    }
    .status-done {
        color: #10b981;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────
st.markdown(
    """
<div class="main-header">
    <h1>🚀 Marketing Campaign Brief Generator</h1>
    <p>Powered by a team of AI agents — Market Researcher, Messaging Strategist, 
    Ad Copywriter, Visual Suggester, and Campaign Formatter</p>
</div>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────
# Async runner function that captures intermediate events
# ──────────────────────────────────────────────────────────
async def run_campaign_agents(
    business_idea: str,
    trace_placeholder,
    status_placeholder,
) -> str:
    """
    Runs the root_agent (CampaignOrchestrator) on the given business idea.
    Captures ALL intermediate events for display in the trace panel, and
    returns the final formatted campaign brief.
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=root_agent.name,
        user_id="streamlit_user",
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=session.app_name,
    )

    trace_lines: list[str] = []
    final_response = ""
    current_agent = ""

    try:
        async for event in runner.run_async(
            user_id="streamlit_user",
            session_id=session.id,
            new_message=Content(parts=[Part(text=business_idea)], role="user"),
        ):
            # ── Capture intermediate trace info ──
            # Extract the author (agent name) from the event
            author = getattr(event, "author", None) or "System"

            # Track agent transitions
            if author != current_agent:
                current_agent = author
                trace_lines.append(f"\n🔄 **Agent: {current_agent}**")
                status_placeholder.markdown(
                    f'<span class="status-running">⏳ Running: {current_agent}...</span>',
                    unsafe_allow_html=True,
                )

            # Capture event content
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        # Truncate very long text for the trace view
                        display_text = part.text
                        if len(display_text) > 500:
                            display_text = display_text[:500] + "... (truncated)"
                        trace_lines.append(f"  📝 `{author}`: {display_text}")
                    elif hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        trace_lines.append(
                            f"  🔧 `{author}` called tool: **{fc.name}**"
                        )
                    elif hasattr(part, "function_response") and part.function_response:
                        fr = part.function_response
                        trace_lines.append(f"  ✅ Tool response for: **{fr.name}**")

            # Update the trace display in real-time
            trace_placeholder.markdown("\n\n".join(trace_lines))

            # ── Capture final response ──
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                else:
                    final_response = (
                        f"Agent finished with reason: "
                        f"{getattr(event, 'finish_reason', 'Unknown')}"
                    )

    except Exception as e:
        final_response = f"❌ An error occurred: {e}"
        trace_lines.append(f"\n❌ **Error**: {e}")
        trace_placeholder.markdown("\n\n".join(trace_lines))

    status_placeholder.markdown(
        '<span class="status-done">✅ All agents completed!</span>',
        unsafe_allow_html=True,
    )

    return final_response


# ──────────────────────────────────────────────────────────
# Sidebar — Agent Pipeline Info
# ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 Agent Pipeline")
    st.markdown(
        """
    Your business idea flows through these agents **sequentially**:

    1. **🔍 MarketResearcher**  
       Searches the web for market insights
       
    2. **💬 MessagingStrategist**  
       Crafts core messages & value propositions
       
    3. **✍️ AdCopywriter**  
       Writes ad copy for multiple channels
       
    4. **🎨 VisualSuggester**  
       Suggests visual concepts for campaigns
       
    5. **📋 CampaignBriefFormatter**  
       Compiles everything into a polished brief
    """
    )
    st.divider()
    st.markdown("### ⚙️ Configuration")
    st.markdown(
        """
    - **Model**: OpenAI `gpt-4o` (via LiteLLM)
    - **Web Search**: Tavily API  
    - **Orchestrator**: ADK `SequentialAgent`
    """
    )


# ──────────────────────────────────────────────────────────
# Main Input Area
# ──────────────────────────────────────────────────────────
st.markdown("### 💡 Enter Your Business Idea")

business_idea = st.text_area(
    label="Describe your product or business idea",
    placeholder=(
        "Example: An AI-powered personal finance app that helps "
        "millennials track spending, set savings goals, and invest "
        "spare change automatically."
    ),
    height=120,
    label_visibility="collapsed",
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run_button = st.button(
        "🚀 Generate Campaign Brief",
        type="primary",
        use_container_width=True,
        disabled=not business_idea.strip(),
    )


# ──────────────────────────────────────────────────────────
# Run the agents when the button is clicked
# ──────────────────────────────────────────────────────────
if run_button and business_idea.strip():

    st.divider()

    # Status indicator
    status_placeholder = st.empty()
    status_placeholder.markdown(
        '<span class="status-running">⏳ Starting agent pipeline...</span>',
        unsafe_allow_html=True,
    )

    # ── Collapsible section for intermediate agent traces ──
    with st.expander(
        "🔬 Agent Trace — Intermediate Output (click to expand)", expanded=False
    ):
        trace_placeholder = st.empty()
        trace_placeholder.markdown("*Waiting for agent events...*")

    # ── Run the async pipeline ──
    with st.spinner("Agents are working on your campaign brief..."):
        final_output = asyncio.run(
            run_campaign_agents(
                business_idea=business_idea.strip(),
                trace_placeholder=trace_placeholder,
                status_placeholder=status_placeholder,
            )
        )

    # ── Display the final campaign brief ──
    st.markdown("---")
    st.markdown("### 📋 Your Marketing Campaign Brief")

    if final_output.startswith("❌"):
        st.error(final_output)
    else:
        st.markdown(final_output)

    # ── Download button ──
    st.download_button(
        label="📥 Download as Markdown",
        data=final_output,
        file_name="campaign_brief.md",
        mime="text/markdown",
    )
