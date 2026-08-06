"""Console & Web Execution Runner for Google ADK 2.5.0."""

import asyncio
import json
from app import app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


async def execute_loan_workflow():
    session_service = InMemorySessionService()
    runner = Runner(app=app, session_service=session_service)

    user_id = "officer_101"
    session_id = "loan_session_8892"

    print("--- PHASE 1: Running Credit & Risk Analysis ---")
    invocation_id = None
    pause_payload = None

    # Step 1: Start Initial Execution Loop
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        input="Process loan application for Jane Doe",
    ):
        # Capture ADK pause event & store invocation ID
        if event.long_running_tool_ids:
            invocation_id = event.invocation_id

        # Extract findings to display to loan officer
        session = await session_service.get_session(
            app_name=app.name, user_id=user_id, session_id=session_id
        )
        if "risk_assessment" in session.state:
            pause_payload = {
                "credit": session.state.get("credit_report"),
                "risk": session.state.get("risk_assessment"),
            }

    # Step 2: Display Summary to Human Loan Officer
    print("\n=======================================================")
    print(" PIPELINE PAUSED: Awaiting Loan Officer Input")
    print("=======================================================")
    print(json.dumps(pause_payload, indent=2))
    print(f"Active Invocation ID: {invocation_id}\n")

    # Step 3: Accept Human Response (Console input or Web HTTP POST)
    # The pipeline can wait here indefinitely (hours/days)
    user_decision = ""
    while user_decision not in ["APPROVE", "REJECT", "REFER"]:
        user_decision = (
            input("Enter Action (APPROVE / REJECT / REFER): ").strip().upper()
        )

    print("\n--- PHASE 2: Resuming Pipeline Execution ---")

    # Step 4: Resume Pipeline using invocation_id and payload
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        invocation_id=invocation_id,
        resume_input={"decision": user_decision},
    ):
        if event.is_final():
            print("\n=======================================================")
            print(" FINAL PIPELINE OUTPUT:")
            print("=======================================================")
            print(event.content)


if __name__ == "__main__":
    asyncio.run(execute_loan_workflow())
