import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv(override=True)
openai_model = LiteLlm(model="openai/gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
