from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

openai_model = LiteLlm(model="openai/gpt-4o")


customer_service_agent = Agent(
    model=openai_model,
    name="root_agent",
    description="A helpful assistant for user questions.",
    instruction="Answer user questions to the best of your knowledge",
)
