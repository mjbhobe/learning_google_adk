from dotenv import load_dotenv
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.models import Gemini  # Use the Gemini wrapper
from google.adk.tools import google_search

from structured_output_agent.tools import get_live_weather_global, web_search
from structured_output_agent.logger import get_logger

load_dotenv(override=True)
# Initialize agent-level logger
logger = get_logger("tool_agent.agent")

gemini_model = Gemini(
    model="gemini-2.5-flash",
    use_interactions_api=True,  # <--- This unlocks tool calling for 2.5+
    bypass_multi_tools_limit=True,  #  <---  unlocks the multi-tool restriction
    # however, you STILL cannot mix internal tools (such as google_search) with
    # your own custom tools!
)


# ---- structured o/p definition --------------
# --- Define Output Schema ---
class EmailContent(BaseModel):
    subject: str = Field(
        description="The subject line of the email. Should be concise and descriptive."
    )
    body: str = Field(
        description="The main content of the email. Should be well-formatted with proper greeting, paragraphs, and signature."
    )


openai_model = LiteLlm(model="openai/gpt-4o")

root_agent = LlmAgent(
    name="structured_output_agent",
    model=openai_model,
    instruction="""
        You are an Email Generation Assistant.
        Your task is to generate a professional email based on the user's request.

        GUIDELINES:
        - Create an appropriate subject line (concise and relevant)
        - Write a well-structured email body with:
            * Professional greeting
            * Clear and concise main content
            * Appropriate closing
            * Your name as signature
        - Suggest relevant attachments if applicable (empty list if none needed)
        - Email tone should match the purpose (formal for business, friendly for colleagues and relatives)
        - For names relatives (such as wife, son, daughter, sister, brother etc.) keep the tone of email very informal and conversational.
        - Keep emails concise but complete

        IMPORTANT: Your response MUST be valid JSON matching this structure:
        {
            "subject": "Subject line here",
            "body": "Email body here with proper paragraphs and formatting",
        }

        DO NOT include any explanations or additional text outside the JSON response.
    """,
    description="Generates professional emails with structured subject and body",
    output_schema=EmailContent,
    output_key="email",
)


"""
gemini-2.5-flash give tool calling not supported error. Here is a fix, as suggested by Google Gemini

from google.adk.models import Gemini # Use the Gemini wrapper

root_agent = Agent(
    name="tool_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True  # <--- This unlocks tool calling for 2.5+
        bypass_multi_tools_limit=True  #  <---  unlocks the multi-tool restriction
    ),
    description="Agent that can use tools",
    instruction=""" """
    You are a helpful travel guide who can provide weather information.
    Use 'get_live_weather_global' to fetch weather information. For any other queries, use
    'google_search' tool to find relevant information. 
    Always provide a helpful response to the user.
    """ """,
    tools=[get_live_weather_global, google_search],
)

How the Model Uses Both
With this setup, if a user asks: "What's the weather in London and can you find me a good Italian restaurant there?", the agent performs Parallel Tool Calling:

It triggers get_live_weather_global(location_name="london").

Simultaneously, it triggers Google Search(query="best Italian restaurants in London").

It merges both outputs into a single, grounded response.

Important 2026 Constraints
Billing: When using Google Search in this "mixed mode," you are billed for the model tokens plus a small flat fee per search query executed (if you are on a paid tier).

Vertex AI vs AI Studio: If you use an AI Studio API key, ensure your .env has GOOGLE_GENAI_USE_VERTEXAI=FALSE. If you are using Google Cloud Vertex AI, set it to TRUE.

Search Suggestions: The model will return "Search Suggestions" (chips) at the bottom of the response when using Google Search. The ADK handles rendering these if you are using the built-in adk web UI.

"""
