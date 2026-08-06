"""ADK Root App Configuration."""

from domain import loan_pipeline
from google.adk.apps import App, ResumabilityConfig

# Master ADK App instance used by both CLI and Streamlit runners
app = App(
    name="LoanApprovalApp",
    root_agent=loan_pipeline,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
