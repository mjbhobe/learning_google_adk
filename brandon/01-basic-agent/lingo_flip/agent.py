from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

openai_model = LiteLlm(model="openai/gpt-4o")

root_agent = Agent(
    model=openai_model,
    name="lingo_flip",
    description="Gen Z lingo generator",
    instruction="""
    You are a helpful assistant that helps translate simple sentences into GenZ lingo, which would be
    of real help to Boomers, Gen X and Millenials 👍
    You will receive a query in simple English, which you need to convert to Gen Z lingo - use Gen Z
    phrases liberally, but please explain what they mean to a Millenial the first time you use it 😊
    """,
)
