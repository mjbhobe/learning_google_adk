from __future__ import annotations

from stock_analysis_adk.utils.formatting import safe_json


def build_markdown_report(symbol: str, raw_sections: dict, agent_sections: dict, final_recommendation: str) -> str:
    return f"""# Stock Analysis Report: {symbol}

## 1. Business Fundamentals

### Raw evidence
```json
{safe_json(raw_sections['business'])}
```

### ADK agent analysis
{agent_sections['business']}

---

## 2. Financial Analysis

### Raw calculations
```json
{safe_json(raw_sections['financial'])}
```

### ADK agent analysis
{agent_sections['financial']}

---

## 3. Peer Benchmarking

### Raw comparisons
```json
{safe_json(raw_sections['peer'])}
```

### ADK agent analysis
{agent_sections['peer']}

---

## 4. Sentiment Analysis

### Raw signals
```json
{safe_json(raw_sections['sentiment'])}
```

### ADK agent analysis
{agent_sections['sentiment']}

---

## 5. Overall Recommendation

{final_recommendation}
"""
