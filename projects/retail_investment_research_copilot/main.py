import requests
from dotenv import load_dotenv
from rich.console import Console

MARKET_DATA_URL = "http://127.0.0.1:8101/invoke"
NEWS_URL = "http://127.0.0.1:8102/invoke"
MEMO_URL = "http://127.0.0.1:8103/invoke"

load_dotenv(override=True)


def main() -> None:
    print("Retail Investment Research Copilot")
    ticker = input("Enter ticker (example: MSFT or TCS.NS): ").strip()
    horizon = input("Investment horizon in (example: 3 years): ").strip() or "3 years"
    risk = input("Risk appetite (low/medium/high): ").strip() or "medium"

    market_resp = requests.post(MARKET_DATA_URL, json={"payload": {"ticker": ticker}})
    market_resp.raise_for_status()

    news_resp = requests.post(NEWS_URL, json={"payload": {"ticker": ticker}})
    news_resp.raise_for_status()

    combined_payload = {
        "ticker": ticker,
        "horizon": horizon,
        "risk_appetite": risk,
        "market_data_analysis": market_resp.json()["result"],
        "news_analysis": news_resp.json()["result"],
    }

    console = Console()
    console.print(f"Combined Payload to Memo Service -> {combined_payload}")

    memo_resp = requests.post(MEMO_URL, json={"payload": combined_payload})
    memo_resp.raise_for_status()
    console.print("\n" + memo_resp.json()["result"])


if __name__ == "__main__":
    main()
