#!/usr/bin/env bash
# --------------------------------------------------------
# helper script to startup & shutdown the uvicorn servers
# for each agent. 
# Do a chmod u+x servers.sh
# then ./servers.sh  -- to run in dedicated terminal
# Press Ctrl+C to terminate all the servers
# --------------------------------------------------------


# Array to store process IDs
PIDS=()

# Function to kill all processes on exit
cleanup() {
    echo -e "\nShutting down all agents..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null
    done
    exit
}

# Execute cleanup function if script is interrupted (Ctrl+C) or terminated
trap cleanup SIGINT SIGTERM

echo "Starting FastAPI Agents..."

# Start each agent and store its PID ($!)
uvicorn agents.host_agent.__main__:app --port 8000 &
PIDS+=($!)

uvicorn agents.flight_agent.__main__:app --port 8001 &
PIDS+=($!)

uvicorn agents.stay_agent.__main__:app --port 8002 &
PIDS+=($!)

uvicorn agents.activities_agent.__main__:app --port 8003 &
PIDS+=($!)

echo "All agents are running. Press [CTRL+C] to stop all of them."

# Keep the script alive so the trap stays active
wait