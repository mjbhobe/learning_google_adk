import ipywidgets as widgets
from IPython.display import display, clear_output

# Initial Data from your CMO Report
data = {
    "Classic Chinos": {"orders": 120, "aov": 85, "ret_rate": 0.20, "ret_cost": 12.50},
    "Slim-Fit Denim": {"orders": 200, "aov": 110, "ret_rate": 0.28, "ret_cost": 14.00},
    "Corduroy Slacks": {"orders": 85, "aov": 95, "ret_rate": 0.20, "ret_cost": 12.50},
    "Baggy Cargo": {"orders": 450, "aov": 140, "ret_rate": 0.36, "ret_cost": 15.00},
    "Wool Dress Trousers": {
        "orders": 110,
        "aov": 125,
        "ret_rate": 0.30,
        "ret_cost": 13.50,
    },
}


def calculate_impact(cargo_ret_target, premium_ret_target, logistics_reduction):
    total_net_profit_gain = 0
    total_return_savings = 0
    total_retained_revenue_gain = 0

    for cat, stats in data.items():
        # Change 1: Baggy Cargo Return Rate
        if cat == "Baggy Cargo":
            old_rets = stats["orders"] * stats["ret_rate"]
            new_rets = stats["orders"] * (cargo_ret_target / 100)

            # Savings from fewer return shipments
            shipment_savings = (old_rets - new_rets) * (
                stats["ret_cost"] - logistics_reduction
            )
            # Revenue retained (assuming 100% refund on returns)
            rev_retained = (old_rets - new_rets) * stats["aov"]

            total_return_savings += shipment_savings
            total_retained_revenue_gain += rev_retained

        # Change 2: Sizing tools for Denim & Wool
        elif cat in ["Slim-Fit Denim", "Wool Dress Trousers"]:
            old_rets = stats["orders"] * stats["ret_rate"]
            new_rets = stats["orders"] * (premium_ret_target / 100)

            shipment_savings = (old_rets - new_rets) * (
                stats["ret_cost"] - logistics_reduction
            )
            rev_retained = (old_rets - new_rets) * stats["aov"]

            total_return_savings += shipment_savings
            total_retained_revenue_gain += rev_retained

        # Change 3: Logistics optimization for all (Cost per Return reduction)
        else:
            current_rets = stats["orders"] * stats["ret_rate"]
            total_return_savings += current_rets * logistics_reduction

    total_gain = total_return_savings + total_retained_revenue_gain

    print(f"--- 2026 PROFIT IMPACT PROJECTION ---")
    print(f"Logistics Cost Savings:     ${total_return_savings:,.2f}")
    print(f"Retained Sales Revenue:     ${total_retained_revenue_gain:,.2f}")
    print(f"=====================================")
    print(f"TOTAL PROFIT INCREASE:      ${total_gain:,.2f}")
    print(f"=====================================")


# Interactive UI Components
style = {"description_width": "initial"}

cargo_slider = widgets.FloatSlider(
    value=36, min=15, max=36, step=1, description="Baggy Cargo Return %:", style=style
)
premium_slider = widgets.FloatSlider(
    value=30, min=15, max=30, step=1, description="Denim/Wool Return %:", style=style
)
logistics_toggle = widgets.FloatSlider(
    value=0,
    min=0,
    max=5,
    step=0.5,
    description="Logistics Savings ($/unit):",
    style=style,
)

ui = widgets.VBox([cargo_slider, premium_slider, logistics_toggle])
out = widgets.interactive_output(
    calculate_impact,
    {
        "cargo_ret_target": cargo_slider,
        "premium_ret_target": premium_slider,
        "logistics_reduction": logistics_toggle,
    },
)

display(ui, out)
