import asyncio
import os
import uuid
from dotenv import load_dotenv
import requests
from rich.console import Console
from rich.markdown import Markdown

from logger import get_logger
from utils import is_valid_stock_symbol, get_stock_info

load_dotenv(override=True)
assert os.getenv(
    "ANTHROPIC_API_KEY"
), "FATAL ERROR: ANTHROPIC_API_KEY not found in .env file!"

logger = get_logger("buffet_stock_analyser.main")

HOST_AGENT_URL = os.getenv("HOST_AGENT_URL", "http://localhost:8000/run")

async def main():
    console = Console()

    symbol = ""

    while True:
        console.print(
            "[yellow]Enter Stock Symbol (e.g., TSLA, GOOGL) or exit to quit: [/yellow]",
            end="",
        )
        symbol = input().strip().upper()

        if symbol.lower() == "exit":
            break
        
        if not is_valid_stock_symbol(symbol):
            console.print(f"[red]Invalid stock symbol: {symbol}. Please try again.[/red]")
            continue

        company_info, raw_financials = get_stock_info(symbol)
        payload = {
            "symbol": symbol,
            "company_info": company_info,
            "raw_financials": raw_financials,
        }
        logger.info(f"payload -> \n{payload}")

        response = requests.post(HOST_AGENT_URL, json=payload)
        if response.ok:
            data = response.json()['formatted_report']
            logger.info(f"Response from agent:\n {data}")
            console.print(Markdown(data['analysis_report']))
        else:
            console.print(f"[red]Failed to fetch analysis for {symbol}. Please try again.[/red]")

if __name__ == "__main__":
    asyncio.run(main())
