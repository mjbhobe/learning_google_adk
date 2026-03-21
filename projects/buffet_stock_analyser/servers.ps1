# -----------------------------------------------------------------------
# servers.ps1 — Windows PowerShell equivalent of servers.sh
#
# Starts the Uvicorn agent service for buffet_stock_analyser.
# Run from the buffet_stock_analyser\ directory:
#
#   .\servers.ps1
#
# Press Ctrl+C to stop the service.
# -----------------------------------------------------------------------

$ErrorActionPreference = "Stop"

# Collect process objects so we can clean up on exit
$Procs = @()

function Stop-Agents {
    Write-Host "`nShutting down all agents..." -ForegroundColor Yellow
    foreach ($proc in $Procs) {
        if (-not $proc.HasExited) {
            $proc.Kill()
        }
    }
}

# Register Ctrl+C handler
[Console]::TreatControlCAsInput = $false
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-Agents }

try {
    Write-Host "Starting FastAPI Agent Service..." -ForegroundColor Cyan

    # Start uvicorn and capture the process object
    $proc = Start-Process `
        -FilePath "uvicorn" `
        -ArgumentList "buffet_bot.agents.__main__:app", "--port", "8000" `
        -NoNewWindow `
        -PassThru

    $Procs += $proc

    Write-Host "Agent service running on http://localhost:8000" -ForegroundColor Green
    Write-Host "Press [Ctrl+C] to stop." -ForegroundColor Gray

    # Wait for the process to exit (keeps the script alive)
    $proc.WaitForExit()
}
finally {
    Stop-Agents
}
