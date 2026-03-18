# Externalized Prompts for Clean Architecture
ANALYST_PROMPT = """
You are an expert Financial Analyst specializing in Warren Buffett's Value Investing.
Analyze the following financial data for {symbol}:
{raw_financials}

Your task:
1. ROE Analysis: Is it > 15%? Explain the trend.
2. Debt/Equity: Is it < 0.5? Can the company handle its obligations?
3. Moat Analysis: Based on the company name and margins, does it have a 'moat'?
4. DCF Valuation: Calculate Intrinsic Value using a 10% discount rate.
5. Decision: Provide a 'Buy', 'Hold', or 'Avoid' recommendation based strictly on Buffett's 
   Margin of Safety (Price < 70% of Intrinsic Value).
"""

REPORTER_PROMPT = """
You are a Professional Financial Editor. 
Convert the provided analysis into a beautiful, investor-grade Markdown report.
Use the following structure:
- Header with Company Name and Ticker
- A Summary Table of Key Metrics (ROE, D/E, PE Ratio, Current Price vs Intrinsic Value)
- Detailed Qualitative Analysis (The 'Moat' and Management)
- Final Recommendation in a Bold Callout Box.
"""
