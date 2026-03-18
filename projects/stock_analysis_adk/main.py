from rich.console import Console
from stock_analysis_adk.tools.metrics_tools import build_metrics_payload


def main():
    console = Console()
    business_payload = build_metrics_payload("AAPL")
    console.print(business_payload)


if __name__ == "__main__":
    main()
