import asyncio
import os
import uuid
from dotenv import load_dotenv
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from google.adk.sessions import InMemorySessionService

from logger import get_logger
from buffet_bot.agent import root_agent as workflow
from utils import get_stock_info, run_agent_query

load_dotenv(override=True)
assert os.getenv(
    "ANTHROPIC_API_KEY"
), "FATAL ERROR: ANTHROPIC_API_KEY not found in .env file!"

logger = get_logger("buffet_stock_analyser.main")


async def main():
    console = Console()
    session_service = InMemorySessionService()

    app_name = Path(__file__).parent.resolve().name
    user_id = "buffet_analyst_007"
    session_id = str(uuid.uuid4())

    symbol = ""

    while True:
        console.print(
            "[yellow]Enter Stock Symbol (e.g., TSLA, GOOGL) or exit to quit: [/yellow]",
            end="",
        )
        symbol = input().strip().upper()

        if symbol.lower() == "exit":
            break

        company_info, raw_financials = get_stock_info(symbol)
        initial_state = {
            "symbol": symbol,
            "company_info": company_info,
            "raw_financials": raw_financials,
        }

        # check if session with session_id already exists
        my_session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

        if my_session is None:
            # create a new session
            my_session = await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state=initial_state,
            )
            logger.info(
                f"\n Created session for first time, with initial_state = {initial_state}\n"
            )
        else:
            # session exists!
            # set the state to the new initial_state
            my_session.state = initial_state
            logger.info(
                f"\n Session already exists! Updated state to = {my_session.state}\n"
            )

        final_markdown_report = await run_agent_query(
            agent=workflow,
            session_service=session_service,
            app_name=app_name,
            user_id=user_id,
            user_query=f"Analyse the stock {symbol}",
            session=my_session,
        )

        console.print("\n[bold green]Agent Response:[/bold green]")
        console.print(Markdown(final_markdown_report))


if __name__ == "__main__":
    asyncio.run(main())
