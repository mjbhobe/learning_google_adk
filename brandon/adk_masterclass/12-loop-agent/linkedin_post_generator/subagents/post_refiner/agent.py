"""
LinkedIn Post Generator Agent

This agent generates the initial LinkedIn post before refinement.
"""

from dotenv import load_dotenv
import logging

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

load_dotenv()

openai_model = LiteLlm(model="openai/gpt-4o")

post_refiner = Agent(
    name="post_refiner",
    model=openai_model,
    instruction="""You are a LinkedIn Post Refiner.

    Your task is to refine a LinkedIn post based on review feedback.
    
    ## INPUTS
    **Current Post:**
    {current_post}
    
    **Review Feedback:**
    {review_feedback}
    
    ## TASK
    Carefully apply the feedback to improve the post.
    - Maintain the original tone and theme of the post
    - Ensure all content requirements are met:
      1. Excitement about learning from the tutorial
      2. Specific aspects of ADK learned (at least 4)
      3. Brief statement about improving AI applications
      4. Mention/tag of @aiwithbrandon
      5. Clear call-to-action for connections
    - Adhere to style requirements:
      - Professional and conversational tone
      - Between 1000-1500 characters
      - NO emojis
      - NO hashtags
      - Show genuine enthusiasm
      - Highlight practical applications
    
    ## OUTPUT INSTRUCTIONS
    - Output ONLY the refined post content
    - Do not add explanations or justifications
    """,
    description="Refines LinkedIn posts based on feedback to improve quality",
    output_key="current_post",
)
