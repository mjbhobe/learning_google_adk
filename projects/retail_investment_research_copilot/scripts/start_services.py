import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SERVICES = [
    ("market-data-service", "agents.market_data_service.service_app", 8101),
    ("news-service", "agents.news_service.service_app", 8102),
    ("memo-service", "agents.memo_service.service_app", 8103),
]

def main() -> None:
    processes = []
    try:
        for name, module, port in SERVICES:
            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                f"{module}:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--reload",
            ]
            print(f"Starting {name} on port {port}...")
            processes.append(subprocess.Popen(cmd, cwd=ROOT))
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\nStopping agents...")
    finally:
        for proc in processes:
            proc.kill()

if __name__ == "__main__":
    main()
