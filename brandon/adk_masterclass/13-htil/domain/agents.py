"""Domain Agents and Sequential Pipeline Assembly."""

from domain.tools import (
    calculate_risk_score,
    draft_underwriter_note,
    generate_pdf_offer,
    hold_for_loan_officer,
    pull_credit_data,
)
from google.adk.agents import Agent, SequentialAgent
from google.adk.models import Gemini

MODEL_NAME = "gemini-3.5-flash-lite"
llm = Gemini(model=MODEL_NAME)

credit_agent = Agent(
    name="CreditAgent",
    model=llm,
    instruction="Pull applicant credit details using pull_credit_data.",
    tools=[pull_credit_data],
)

risk_agent = Agent(
    name="RiskAgent",
    model=llm,
    instruction="Evaluate risk metrics using calculate_risk_score.",
    tools=[calculate_risk_score],
)

review_agent = Agent(
    name="ReviewAgent",
    model=llm,
    instruction="Call hold_for_loan_officer to present findings.",
    tools=[hold_for_loan_officer],
)

approval_agent = Agent(
    name="ApprovalAgent",
    model=llm,
    instruction="Generate loan offer PDF using generate_pdf_offer.",
    tools=[generate_pdf_offer],
)

referral_agent = Agent(
    name="ReferralAgent",
    model=llm,
    instruction="Draft senior underwriter escalation using draft_underwriter_note.",
    tools=[draft_underwriter_note],
)

fulfillment_agent = Agent(
    name="FulfillmentAgent",
    model=llm,
    sub_agents=[approval_agent, referral_agent],
    instruction="""
    Examine 'officer_decision' in session state:
    - If 'APPROVE': Delegate task to ApprovalAgent.
    - If 'REFER': Delegate task to ReferralAgent.
    - If 'REJECT': State that the application is rejected.
    """,
)

loan_pipeline = SequentialAgent(
    name="LoanProcessingPipeline",
    sub_agents=[credit_agent, risk_agent, review_agent, fulfillment_agent],
)
