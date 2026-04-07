from typing import Dict, Any, List

from tools.db_tools import run_sql_query


def build_root_cause_prompt(question: str, db_path: str):
    diagnostics = {}
    telemetry = {
        "timing": {},
        "quality": {
            "status": "success",
            "diagnostic_queries_attempted": 0,
            "diagnostic_queries_succeeded": 0,
        }
    }

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
        telemetry["quality"]["diagnostic_queries_attempted"] += 1
        try:
            result = run_sql_query(db_path, query)
            diagnostics[name] = {
                "query": query.strip(),
                "rows": result["rows"],
                "row_count": len(result["rows"]),
            }
            telemetry["timing"][f"{name}_sec"] = result["telemetry"]["timing"]["sql_execution_sec"]
            telemetry["quality"]["diagnostic_queries_succeeded"] += 1
        except Exception as e:
            diagnostics[name] = {
                "query": query.strip(),
                "error": str(e),
                "rows": []
            }

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
    return prompt, diagnostics, telemetry


def build_recommendation_context(question: str, db_path: str) -> Dict[str, Any]:
    snippets = []
    query_logs = []
    telemetry = {
        "timing": {},
        "quality": {
            "status": "success",
            "analytics_queries_attempted": 0,
            "analytics_queries_succeeded": 0,
        }
    }

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

    for idx, q in enumerate(candidate_queries, start=1):
        telemetry["quality"]["analytics_queries_attempted"] += 1
        try:
            result = run_sql_query(db_path, q)
            rows = result["rows"]
            snippets.append(str(rows[:10]))
            query_logs.append({
                "name": f"analytics_query_{idx}",
                "query": q.strip(),
                "row_count": len(rows),
                "preview": rows[:5],
            })
            telemetry["timing"][f"analytics_query_{idx}_sec"] = result["telemetry"]["timing"]["sql_execution_sec"]
            telemetry["quality"]["analytics_queries_succeeded"] += 1
        except Exception as e:
            snippets.append(f"Query failed: {e}")
            query_logs.append({
                "name": f"analytics_query_{idx}",
                "query": q.strip(),
                "error": str(e),
                "row_count": 0,
                "preview": [],
            })

    return {
        "context": "\n\n".join(snippets),
        "query_logs": query_logs,
        "telemetry": telemetry
    }