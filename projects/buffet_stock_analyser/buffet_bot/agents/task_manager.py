"""
task_manager.py (for the main workflow agent)

Executes the sequence worflow by calling execute
"""

from logger import get_logger

from .agent import execute

logger = get_logger("buffet_stock_analyser.agents.task_manager")

async def run(payload):
    # display input we got
    logger.info(f"Workflow agent task_manager -> incoming payload: \n {payload}")
    formatted_report = await execute(payload)
    logger.info(f"Workflow agent task_manager -> formatted_report: \n {formatted_report}")
    return {
        "formatted_report": formatted_report,
    }
