from google.adk.agents import ParallelAgent, SequentialAgent

from stock_analysis_adk.agents.business_fundamentals_agent import create_business_fundamentals_agent
from stock_analysis_adk.agents.financial_analysis_agent import create_financial_analysis_agent
from stock_analysis_adk.agents.peer_benchmark_agent import create_peer_benchmark_agent
from stock_analysis_adk.agents.sentiment_analysis_agent import create_sentiment_analysis_agent
from stock_analysis_adk.agents.recommendation_agent import create_recommendation_agent


business_agent = create_business_fundamentals_agent()
financial_agent = create_financial_analysis_agent()
peer_agent = create_peer_benchmark_agent()
sentiment_agent = create_sentiment_analysis_agent()
recommendation_agent = create_recommendation_agent()

parallel_analysis_agent = ParallelAgent(
    name="parallel_analysis_agent",
    sub_agents=[business_agent, financial_agent, peer_agent, sentiment_agent],
)

root_agent = SequentialAgent(
    name="root_agent",
    sub_agents=[parallel_analysis_agent, recommendation_agent],
)
