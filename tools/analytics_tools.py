from typing import Dict, Any, List

from tools.db_tools import run_sql_query


def build_root_cause_prompt(question: str, db_path: str):
    diagnostics = {}

    queries = {
        "late_delivery_overall": """
            SELECT
                AVG(CASE WHEN is_late_delivery = 1 THEN 1.0 ELSE 0.0 END) AS late_delivery_rate,
                AVG(delivery_days) AS avg_delivery_days,
                AVG(delivery_delay_days) AS avg_delivery_delay_days
            FROM orders
            WHERE is_delivered = 1;
        """,
        "review_overall": """
            SELECT
                AVG(review_score) AS avg_review_score,
                AVG(CASE WHEN is_satisfied = 1 THEN 1.0 ELSE 0.0 END) AS satisfied_rate
            FROM review_orders;
        """,
        "seller_risk": """
            SELECT
                oi.seller_id,
                COUNT(DISTINCT oi.order_id) AS order_count,
                AVG(o.is_late_delivery) AS late_delivery_rate,
                AVG(ro.review_score) AS avg_review_score,
                AVG(oi.freight_ratio) AS avg_freight_ratio
            FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN review_orders ro ON oi.order_id = ro.order_id
            GROUP BY oi.seller_id
            HAVING COUNT(DISTINCT oi.order_id) >= 20
            ORDER BY avg_review_score ASC, late_delivery_rate DESC
            LIMIT 10;
        """,
        "category_risk": """
            SELECT
                p.product_category_name_english,
                COUNT(DISTINCT oi.order_id) AS order_count,
                AVG(o.is_late_delivery) AS late_delivery_rate,
                AVG(ro.review_score) AS avg_review_score,
                AVG(oi.freight_ratio) AS avg_freight_ratio
            FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN review_orders ro ON oi.order_id = ro.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_category_name_english
            HAVING COUNT(DISTINCT oi.order_id) >= 20
            ORDER BY avg_review_score ASC, late_delivery_rate DESC
            LIMIT 10;
        """
    }

    for name, query in queries.items():
        try:
            diagnostics[name] = run_sql_query(db_path, query)
        except Exception as e:
            diagnostics[name] = [{"error": str(e)}]

    prompt = f"""
You are a commerce root-cause analyst.

User question:
{question}

Use the diagnostics below to identify likely drivers.
Do not claim certainty when the data only suggests hypotheses.
Rank the most plausible drivers and explain them clearly.

Diagnostics:
{diagnostics}
"""
    return prompt, diagnostics


def build_recommendation_context(question: str, db_path: str) -> str:
    snippets = []

    candidate_queries = [
        """
        SELECT
            COUNT(*) AS total_orders,
            AVG(CASE WHEN is_late_delivery = 1 THEN 1.0 ELSE 0.0 END) AS late_delivery_rate,
            AVG(delivery_days) AS avg_delivery_days
        FROM orders
        WHERE is_delivered = 1;
        """,
        """
        SELECT
            AVG(review_score) AS avg_review_score,
            AVG(CASE WHEN is_satisfied = 1 THEN 1.0 ELSE 0.0 END) AS satisfied_rate
        FROM review_orders;
        """,
        """
        SELECT
            p.product_category_name_english,
            SUM(oi.total_item_value) AS revenue,
            AVG(oi.freight_ratio) AS avg_freight_ratio
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_category_name_english
        ORDER BY revenue DESC
        LIMIT 10;
        """,
        """
        SELECT
            oi.seller_id,
            COUNT(DISTINCT oi.order_id) AS order_count,
            AVG(o.is_late_delivery) AS late_delivery_rate,
            AVG(ro.review_score) AS avg_review_score
        FROM order_items oi
        LEFT JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN review_orders ro ON oi.order_id = ro.order_id
        GROUP BY oi.seller_id
        HAVING COUNT(DISTINCT oi.order_id) >= 20
        ORDER BY late_delivery_rate DESC, avg_review_score ASC
        LIMIT 10;
        """
    ]

    for q in candidate_queries:
        try:
            rows = run_sql_query(db_path, q)
            snippets.append(str(rows[:10]))
        except Exception as e:
            snippets.append(f"Query failed: {e}")

    return "\n\n".join(snippets)