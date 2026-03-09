"""
System Monitor Root Agent

This module defines the root agent for the system monitoring application.
It uses a parallel agent for system information gathering and a sequential
pipeline for the overall flow.
"""

from dotenv import load_dotenv
import logging

from google.adk.agents import LoopAgent, SequentialAgent

from .subagents.post_generator import initial_post_generator
from .subagents.post_refiner import post_refiner
from .subagents.post_reviewer import post_reviewer

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

load_dotenv()

from .subagents.post_generator import initial_post_generator
from .subagents.post_refiner import post_refiner
from .subagents.post_reviewer import post_reviewer

# Create the Refinement Loop Agent
refinement_loop = LoopAgent(
    name="PostRefinementLoop",
    max_iterations=10,
    sub_agents=[
        post_reviewer,
        post_refiner,
    ],
    description="Iteratively reviews and refines a LinkedIn post until quality requirements are met",
)

# Create the Sequential Pipeline
root_agent = SequentialAgent(
    name="LinkedInPostGenerationPipeline",
    sub_agents=[
        initial_post_generator,  # Step 1: Generate initial post
        refinement_loop,  # Step 2: Review and refine in a loop
    ],
    description="Generates and refines a LinkedIn post through an iterative review process",
)
