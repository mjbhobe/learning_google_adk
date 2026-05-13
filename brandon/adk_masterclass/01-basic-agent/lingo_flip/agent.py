from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

# NOTE: I am attempting to use the cheapest models from
# each provider. You can change it to whichever model you'd like to use

# for OpenAI LLM use following line
model = LiteLlm(model="openai/gpt-5-nano")
# for Google Gemini use this instead (using 3.1 flash lite)
# model = LiteLlm(model="gemini/gemini-3.1-flash-lite")
# for Anthropic Claude Haiku use
# model = LiteLlm(model="anthropic/claude-4-5-haiku")

root_agent = Agent(
    model=model,
    name="lingo_flip",
    description="Gen Z lingo generator",
    instruction="""
    You are a helpful assistant that helps translate simple sentences into GenZ lingo, 
    which would be of real help to Boomers, Gen X and Millenials 👍
    You will receive a query in simple English, which you need to convert to Gen Z lingo 
    - use Gen Z phrases liberally, but please explain what they mean (to a Boomers, Gen X 
    or Millenials) the first time you use it 😊
    """,
)
