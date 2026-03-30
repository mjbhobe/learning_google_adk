from fastapi import FastAPI
from .agent import build_root_agent
from .models import AgentRequest, AgentResponse
from .runtime import run_agent

app = FastAPI(title="Memo Service")

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "memo_service"}

@app.post("/invoke", response_model=AgentResponse)
def invoke(req: AgentRequest) -> AgentResponse:
    agent = build_root_agent()
    if req.prompt:
        prompt = req.prompt
    else:
        prompt = "Analyze this JSON payload and produce the required result:\n\n" + str(req.payload)
    result = run_agent(agent=agent, prompt=prompt, initial_state={"input_payload": req.payload})
    return AgentResponse(result=result, meta={"service": "memo_service"})
