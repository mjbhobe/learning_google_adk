import argparse
from pathlib import Path

from stock_analysis_adk.orchestrator import run_full_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full ADK stock analysis.")
    parser.add_argument("--symbol", required=True, help="Ticker symbol, for example AAPL")
    parser.add_argument("--output", required=False, help="Optional path to save markdown report")
    args = parser.parse_args()

    result = run_full_analysis(args.symbol.upper())
    print(result["report_markdown"])

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result["report_markdown"], encoding="utf-8")


if __name__ == "__main__":
    main()
