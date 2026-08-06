"""Domain Tools for Credit, Risk, and Fulfillment."""

from google.adk.tools import ToolContext


def pull_credit_data(applicant_name: str, tool_context: ToolContext) -> dict:
    """Pulls credit score and financial history."""
    report = {
        "applicant_name": applicant_name,
        "credit_score": 720,
        "annual_income": 95000,
        "requested_amount": 25000,
    }
    tool_context.state["credit_report"] = report
    return report


def calculate_risk_score(tool_context: ToolContext) -> dict:
    """Calculates risk level from stored report."""
    report = tool_context.state.get("credit_report", {})
    score = report.get("credit_score", 600)
    risk_assessment = {"score": score, "risk_level": "LOW"}
    tool_context.state["risk_assessment"] = risk_assessment
    return risk_assessment


async def hold_for_loan_officer(tool_context: ToolContext) -> str:
    """Triggers the ADK pause gate."""
    confirmation = await tool_context.request_confirmation(
        hint="AWAITING_LOAN_OFFICER_REVIEW"
    )
    decision = confirmation.get("decision", "REJECT").upper()
    tool_context.state["officer_decision"] = decision
    return f"Loan Officer decision recorded: {decision}"


def generate_pdf_offer(tool_context: ToolContext) -> str:
    """Generates the PDF loan offer."""
    credit = tool_context.state.get("credit_report", {})
    filename = f"Loan_Offer_{credit.get('applicant_name', 'Applicant')}.pdf"
    tool_context.state["offer_pdf"] = filename
    return f"Generated {filename}"


def draft_underwriter_note(tool_context: ToolContext) -> str:
    """Drafts an escalation memo for senior underwriting."""
    memo = "Escalated for manual review."
    tool_context.state["underwriter_memo"] = memo
    return memo
