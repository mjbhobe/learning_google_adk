import yfinance as yf
from google.adk.agents import BaseAgent


class DataCollectorAgent(BaseAgent):
    """
    Step 1: The Data Collector.
    Uses yfinance to pull raw metrics and stuff them into the session state.
    """

    async def _run_async_impl(self, ctx):
        symbol = ctx.session.state.get("symbol")
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Buffett-specific data extraction
        company_info = {
            "company_name": info.get("longName"),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "description": info.get("longBusinessSummary", "No description available."),
        }

        raw_financials = {
            "symbol": symbol,
            "stock_price": info.get("currentPrice"),
            "return_on_equity": info.get("returnOnEquity"),
            "debt_to_equity_ratio": info.get("debtToEquity", 0) / 100,  # Normalized
            "free_cash_flow": info.get("freeCashflow", 0),
            "price_to_earnings_ratio": info.get("trailingPE"),
            "market_cap": info.get("marketCap"),
            "beta": info.get("beta"),
        }

        # Stuffing values into session state for the LLM to access later
        ctx.session.state["company_info"] = company_info
        ctx.session.state["raw_financials"] = raw_financials
        yield self.event(f"Data for {symbol} successfully cached in session state.")
