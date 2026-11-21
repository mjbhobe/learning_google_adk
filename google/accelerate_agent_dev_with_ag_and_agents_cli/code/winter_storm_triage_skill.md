---
name: winter-storm-triage
description: Standard operating procedures for handling and triaging customer orders 
delayed due to severe winter storms, including loyalty verification, compensation 
calculation, and resolution messaging.
---

# Winter Storm Triage Standard Operating Procedures

This skill guides the agent through managing customer inquiries and triage when packages 
are delayed due to severe winter storms.

## Standard Operating Procedure

### Step 1: Verify Order and Loyalty Information
1. Use the `get_order_status` tool with the provided `order_id` to verify the order 
status, delay reason, and retrieve the customer ID (`customer_id`).
   - Confirm that the delay is caused by severe winter storm disruptions.
2. Use the `get_customer_loyalty_info` tool with the retrieved `customer_id` to determine 
the customer's loyalty tier (`MEMBER`, `SILVER`, `GOLD`, or `PLATINUM`).

### Step 2: Determine Compensation Matrix
Apply compensation and shipping upgrade according to the customer's loyalty tier:

| Loyalty Tier | Compensation Amount | Shipping Upgrade |
|---|---|---|
| **PLATINUM** | $100 | Next-Day Air |
| **GOLD** | $50 | Next-Day Air |
| **SILVER** | $25 | 3-Day Select |
| **MEMBER** | $10 | Priority Shipping |

### Step 3: Issue Disruption Compensation
Call the `issue_disruption_compensation` tool with the following parameters:
- `customer_id`: The verified customer ID
- `compensation_amount`: The amount determined from the tier matrix (e.g., "$100", "$50", 
"$25", "$10")
- `shipping_upgrade`: The shipping upgrade determined from the tier matrix (e.g., 
"Next-Day Air", "3-Day Select", "Priority Shipping")

### Step 4: Draft Empathetic Customer Response
Draft an empathetic and professional customer response detailing the resolution. The 
response must:
- Acknowledge the delay caused by the severe winter storm and apologize for the 
disruption.
- State the compensation credit applied to the customer's account based on their loyalty 
status.
- Specify the shipping upgrade applied to accelerate package delivery once transit routes 
clear.
- Reassure the customer and provide assistance for any further questions.
