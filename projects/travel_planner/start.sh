#!/bin/bash
# start.sh - unified entrypoint that reads SERVICE_TYPE env variable

if [ "$SERVICE_TYPE" == "flight" ]; then
    echo "Starting Flight Agent..."
    exec uvicorn agents.flight_agent.__main__:app --host 0.0.0.0 --port 8080
elif [ "$SERVICE_TYPE" == "stay" ]; then
    echo "Starting Stay Agent..."
    exec uvicorn agents.stay_agent.__main__:app --host 0.0.0.0 --port 8080
elif [ "$SERVICE_TYPE" == "activities" ]; then
    echo "Starting Activities Agent..."
    exec uvicorn agents.activities_agent.__main__:app --host 0.0.0.0 --port 8080
elif [ "$SERVICE_TYPE" == "host" ]; then
    echo "Starting Host Agent..."
    exec uvicorn agents.host_agent.__main__:app --host 0.0.0.0 --port 8080
elif [ "$SERVICE_TYPE" == "streamlit" ]; then
    echo "Starting Streamlit App..."
    exec streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
else
    echo "ERROR: Unknown SERVICE_TYPE: '$SERVICE_TYPE'"
    echo "Please set SERVICE_TYPE to one of: flight, stay, activities, host, streamlit"
    exit 1
fi
