# -----------------------------------------------------------------------
# servers.ps1 — Windows PowerShell script to start the agent service
#
# Run from the buffet_stock_analyser\ directory:
#
#   .\servers.ps1
#
# Press Ctrl+C to stop the service.
# -----------------------------------------------------------------------

Write-Host "Starting FastAPI Agent Service..." -ForegroundColor Cyan
Write-Host "Listening on http://localhost:8000  |  Press Ctrl+C to stop." -ForegroundColor Green

# uv run ensures uvicorn is resolved from the managed venv,
# exactly the same way you run:  uv run main.py
uv run uvicorn buffet_bot.agents.__main__:app --port 8000
