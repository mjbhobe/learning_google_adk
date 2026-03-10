"""
a2a_server.py: Instead of writing a custom FastAPI route for each agent, we
generalize it using the create_app(agent) function, which handles:
    * Serving the agent on /run
    * Receiving a travel request
    * Returning a structured response
"""

from fastapi import FastAPI
import uvicorn


def create_app(agent):
    app = FastAPI()

    @app.post("/run")
    async def run(payload: dict):
        return await agent.execute(payload)

    return app
