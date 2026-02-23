import os
from dotenv import load_dotenv
from rich.console import Console

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from utils import load_agent_config, run_agent_query, web_search


load_dotenv(override=True)
console = Console()

# we'll use the Open AI gpt-4o model across all agents
# NOTE: you can use any of the supported models (& each agent can)
# use a different model.
openai_model = LiteLlm(model="openai/gpt-4o")

# Market Research Assistant
market_assistant_config = load_agent_config("market_research_assistant")

market_research_assistant = LlmAgent(
    name="MarketResearcher",
    model=openai_model,
    description="A Market Researcher",
    instruction=market_assistant_config["instruction"],
    tools=[web_search],
    # write output to this key in session to hand-off to next Agent
    output_key="market_research_summary",
)

# Messaging Strategist
messaging_strategist_config = load_agent_config("messaging_strategist_assistant")

messaging_strategist = LlmAgent(
    name="MessagingStrategist",
    model=openai_model,
    description="A Messaging Strategist",
    instruction=messaging_strategist_config["instruction"],
    # write output to this key in session    to hand-off to next Agent
    output_key="key_messaging",
)

# Ad copywriter agent
ad_copywriter_config = load_agent_config("ad_copywriter_assistant")

ad_copywriter = LlmAgent(
    name="AdCopywriter",
    model=openai_model,
    description="An Ad Copywriter",
    instruction=ad_copywriter_config["instruction"],
    # write output to this key in session to hand-off to next Agent
    output_key="visual_concepts",
)

# Visual Suggester Agent
visual_suggester_config = load_agent_config("visual_suggester_assistant")

visual_suggester = LlmAgent(
    name="VisualSuggester",
    model=openai_model,
    description="A Visual Suggester",
    instruction=visual_suggester_config["instruction"],
    # write output to this key in session to hand-off to next Agent
    output_key="visual_concepts",
)

# -- the formatter agent - final agent in sequence
formatter_config = load_agent_config("formatter_assistant")

formatter_agent = LlmAgent(
    name="CampaignBriefFormatter",
    model=openai_model,
    description="A Campaign Brief Formatter",
    instruction=formatter_config["instruction"],
    # write output to this key in session to hand-off to next Agent
    output_key="final_campaign_brief",
)

# Campaign Orchestrator
campaign_orchestrator_config = load_agent_config("campaign_orchestrator")

campaign_orchestrator = SequentialAgent(
    name="CampaignOrchestrator",
    description=campaign_orchestrator_config["description"],
    sub_agents=[
        market_research_assistant,
        messaging_strategist,
        ad_copywriter,
        visual_suggester,
        formatter_agent,
    ],
)


root_agent = campaign_orchestrator
