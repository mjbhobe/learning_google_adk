"""
LinkedIn Post Generator Agent

This agent generates the initial LinkedIn post before refinement.
"""

from dotenv import load_dotenv
import logging

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools import count_characters, exit_loop

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

load_dotenv()

openai_model = LiteLlm(model="openai/gpt-4o")

post_reviewer = Agent(
    name="post_reviewer",
    model=openai_model,
    instruction="""You are a LinkedIn Post Quality Reviewer.

    Your task is to evaluate the quality of a LinkedIn post about Agent Development Kit (ADK).
    
    ## EVALUATION PROCESS
    1. Use the count_characters tool to check the post's length.
       Pass the post text directly to the tool.
    
    2. If the length check fails (tool result is "fail"), provide specific feedback on what needs to be fixed.
       Use the tool's message as a guideline, but add your own professional critique.
    
    3. If length check passes, evaluate the post against these criteria:
       - REQUIRED ELEMENTS:
         1. Mentions @aiwithbrandon
         2. Lists multiple ADK capabilities (at least 4)
         3. Has a clear call-to-action
         4. Includes practical applications
         5. Shows genuine enthusiasm
       
       - STYLE REQUIREMENTS:
         1. NO emojis
         2. NO hashtags
         3. Professional tone
         4. Conversational style
         5. Clear and concise writing
    
    ## OUTPUT INSTRUCTIONS
    IF the post fails ANY of the checks above:
      - Return concise, specific feedback on what to improve
      
    ELSE IF the post meets ALL requirements:
      - Call the exit_loop function
      - Return "Post meets all requirements. Exiting the refinement loop."
      
    Do not embellish your response. Either provide feedback on what to improve OR call exit_loop and return the completion message.
    
    ## POST TO REVIEW
    {current_post}
    """,
    description="Reviews post quality and provides feedback on what to improve or exits the loop if requirements are met",
    tools=[count_characters, exit_loop],
    output_key="review_feedback",
)
