"""
task_manager.py
    After defining the execute() logic inside agent.py, we now wire
    it up into the ADK-compatible server setup using this file.
"""

from .agent import execute


async def run(payload):
    return await execute(payload)
