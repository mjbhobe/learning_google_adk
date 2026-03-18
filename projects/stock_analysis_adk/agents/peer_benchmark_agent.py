from google.adk.agents import Agent
from stock_analysis_adk.agents.model_factory import make_model
from stock_analysis_adk.tools.peer_tools import build_peer_payload


def create_peer_benchmark_agent() -> Agent:
    return Agent(
        name="peer_benchmark_agent",
        model=make_model(),
        description="Interprets company-vs-peer comparisons computed in Python.",
        instruction=(
            "You are a peer benchmarking specialist. "
            "Do not calculate anything. Use only the precomputed company-vs-peer deltas. "
            "Explain where the company is above, below, or inline with peer medians and why that matters."
        ),
        tools=[build_peer_payload],
    )
