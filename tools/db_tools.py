import re
import sqlite3
import time
from typing import List, Dict, Any

from tools.schema_tools import DATABASE_SCHEMA_TEXT


def _extract_token_usage(response) -> Dict[str, int]:
    usage = getattr(response, "response_metadata", {}).get("token_usage", {}) or {}
    return {
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }


def generate_sql(question: str, llm) -> Dict[str, Any]:
    prompt = f"""
You are an expert SQLite analytics assistant.

Generate only one valid SQLite SELECT query.
Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or PRAGMA.
Only use the schema below.

Schema:
{DATABASE_SCHEMA_TEXT}

Business rules:
- Revenue can usually be approximated using order_items.total_item_value or sum(price + freight_value).
- Late delivery can use orders.is_late_delivery = 1
- Delivered orders can use orders.is_delivered = 1
- Customer satisfaction can use review_orders.review_score and review_orders.is_satisfied
- Seller performance usually joins orders, order_items, review_orders, and sellers
- Product/category analysis usually joins order_items and products
- Payment analysis uses payment_order

Return only SQL.

Question:
{question}
"""
    start = time.perf_counter()
    response = llm.invoke(prompt)
    elapsed = time.perf_counter() - start

    raw = response.content.strip()
    match = re.search(r"(?is)(select\s+.*?;)", raw)
    if not match:
        raise ValueError(f"Could not extract SQL from model output: {raw}")

    sql_query = match.group(1).strip()

    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "pragma "]
    lowered = sql_query.lower()
    if any(x in lowered for x in forbidden):
        raise ValueError("Unsafe SQL detected.")

    return {
        "sql_query": sql_query,
        "telemetry": {
            "timing": {
                "sql_generation_sec": round(elapsed, 4)
            },
            "tokens": _extract_token_usage(response),
            "quality": {
                "status": "success",
                "sql_generated": True
            }
        }
    }


def run_sql_query(db_path: str, query: str) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    start = time.perf_counter()
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        result = [dict(row) for row in rows]
        elapsed = time.perf_counter() - start
        return {
            "rows": result,
            "telemetry": {
                "timing": {
                    "sql_execution_sec": round(elapsed, 4)
                },
                "quality": {
                    "status": "success",
                    "sql_executed": True,
                    "has_results": len(result) > 0
                }
            }
        }
    finally:
        conn.close()


def format_sql_result(question: str, sql_query: str, rows: List[Dict[str, Any]], llm) -> Dict[str, Any]:
    prompt = f"""
You are a business analyst assistant.

User question:
{question}

SQL used:
{sql_query}

Query result rows:
{rows[:20]}

Write a concise but useful answer in plain English.
If rows are empty, say no matching data was found.
If relevant, summarize trends and highlight top insights.
"""
    start = time.perf_counter()
    response = llm.invoke(prompt)
    elapsed = time.perf_counter() - start

    return {
        "answer": response.content,
        "telemetry": {
            "timing": {
                "answer_formatting_sec": round(elapsed, 4)
            },
            "tokens": _extract_token_usage(response),
            "quality": {
                "status": "success"
            }
        }
    }