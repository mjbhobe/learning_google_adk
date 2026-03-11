# start.ps1 - unified entrypoint that reads SERVICE_TYPE env variable

$ServiceType = $env:SERVICE_TYPE

if ($ServiceType -eq "flight") {
    Write-Host "Starting Flight Agent..."
    uvicorn agents.flight_agent.__main__:app --host 0.0.0.0 --port 8080
} elseif ($ServiceType -eq "stay") {
    Write-Host "Starting Stay Agent..."
    uvicorn agents.stay_agent.__main__:app --host 0.0.0.0 --port 8080
} elseif ($ServiceType -eq "activities") {
    Write-Host "Starting Activities Agent..."
    uvicorn agents.activities_agent.__main__:app --host 0.0.0.0 --port 8080
} elseif ($ServiceType -eq "host") {
    Write-Host "Starting Host Agent..."
    uvicorn agents.host_agent.__main__:app --host 0.0.0.0 --port 8080
} elseif ($ServiceType -eq "streamlit") {
    Write-Host "Starting Streamlit App..."
    streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
} else {
    Write-Host "ERROR: Unknown SERVICE_TYPE: '$ServiceType'"
    Write-Host "Please set SERVICE_TYPE to one of: flight, stay, activities, host, streamlit"
    exit 1
}
