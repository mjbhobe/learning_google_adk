from dotenv import load_dotenv
from rich.console import Console

from utils.ratios import (
    is_valid_ticker,
    get_liquidity_ratios,
    get_profitability_ratios,
    get_efficiency_ratios,
    get_valuation_ratios,
    get_leverage_ratios,
    get_performance_and_growth_metrics,
)


session_state = {
    "symbol": "",
    "liquidity_ratios": None,
    "profitability_ratios": None,
    "efficiency_ratios": None,
    "valuation_ratios": None,
    "leverage_ratios": None,
    "performance_and_growth_metrics": None,
}


load_dotenv(override=True)
console = Console()

# let's test the calculations
symbol: str = "RELIANCE.NS"

console.print(f"[yellow]{symbol} is valid? {is_valid_ticker(symbol)}")
liquidity_ratios = get_liquidity_ratios(symbol)
console.print("[blue]Liquidity Ratios:\n[/blue]")
console.print(liquidity_ratios)
profitability_ratios = get_profitability_ratios(symbol)
console.print("[blue]Profitability Ratios:\n[/blue]")
console.print(profitability_ratios)
efficiency_ratios = get_efficiency_ratios(symbol)
console.print("[blue]Efficiency Ratios:\n[/blue]")
console.print(efficiency_ratios)
valuation_ratios = get_valuation_ratios(symbol)
console.print("[blue]Valuation Ratios:\n[/blue]")
console.print(valuation_ratios)
leverage_ratios = get_leverage_ratios(symbol)
console.print("[blue]Leverage Ratios:\n[/blue]")
console.print(leverage_ratios)
performance_and_growth_metrics = get_performance_and_growth_metrics(symbol)
console.print("[blue]Performance and Growth Metrics:\n[/blue]")
console.print(performance_and_growth_metrics)

# initialize sessiion state with all calculations
session_state["symbol"] = symbol
session_state["liquidity_ratios"] = liquidity_ratios
session_state["profitability_ratios"] = profitability_ratios
session_state["efficiency_ratios"] = efficiency_ratios
session_state["valuation_ratios"] = valuation_ratios
session_state["leverage_ratios"] = leverage_ratios
session_state["performance_and_growth_metrics"] = performance_and_growth_metrics




