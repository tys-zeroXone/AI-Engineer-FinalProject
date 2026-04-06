import re
import sqlite3
from typing import List, Dict, Any

from tools.schema_tools import DATABASE_SCHEMA_TEXT


def generate_sql(question: str, llm) -> str:
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
    raw = llm.invoke(prompt).content.strip()

    match = re.search(r"(?is)(select\s+.*?;)", raw)
    if not match:
        raise ValueError(f"Could not extract SQL from model output: {raw}")

    sql_query = match.group(1).strip()

    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "pragma "]
    lowered = sql_query.lower()
    if any(x in lowered for x in forbidden):
        raise ValueError("Unsafe SQL detected.")

    return sql_query


def run_sql_query(db_path: str, query: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        result = [dict(row) for row in rows]
        return result
    finally:
        conn.close()


def format_sql_result(question: str, sql_query: str, rows: List[Dict[str, Any]], llm) -> str:
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
    return llm.invoke(prompt).content