from typing import List, Dict, Any
import time

from langchain_openai import ChatOpenAI

from tools.db_tools import generate_sql, run_sql_query, format_sql_result


def _sum_token_blocks(*blocks) -> Dict[str, int]:
    return {
        "input_tokens": sum((b or {}).get("input_tokens", 0) for b in blocks),
        "output_tokens": sum((b or {}).get("output_tokens", 0) for b in blocks),
        "total_tokens": sum((b or {}).get("total_tokens", 0) for b in blocks),
    }


class SQLAgent:
    def __init__(self, db_path: str, openai_api_key: str):
        self.db_path = db_path
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)

    def run(self, question: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        agent_start = time.perf_counter()

        sql_gen = generate_sql(question=question, llm=self.llm)
        sql_query = sql_gen["sql_query"]

        sql_exec = run_sql_query(db_path=self.db_path, query=sql_query)
        rows = sql_exec["rows"]

        formatted = format_sql_result(
            question=question,
            sql_query=sql_query,
            rows=rows,
            llm=self.llm
        )

        total_elapsed = time.perf_counter() - agent_start

        tokens = _sum_token_blocks(
            sql_gen["telemetry"].get("tokens"),
            formatted["telemetry"].get("tokens"),
        )

        debug = {
            "agent_telemetry": {
                "agent_name": "SQLAgent",
                "timing": {
                    "total_latency_sec": round(total_elapsed, 4),
                    **sql_gen["telemetry"].get("timing", {}),
                    **sql_exec["telemetry"].get("timing", {}),
                    **formatted["telemetry"].get("timing", {}),
                },
                "tokens": tokens,
                "query": {
                    "sql_query": sql_query,
                    "row_count": len(rows),
                    "preview": rows[:10],
                },
                "quality": {
                    "status": "success",
                    "accuracy_note": "Execution-quality telemetry only. True answer accuracy requires benchmark labels.",
                    "sql_generated": True,
                    "sql_executed": True,
                    "has_results": len(rows) > 0,
                }
            }
        }

        return {
            "selected_agent": "SQLAgent",
            "answer": formatted["answer"],
            "debug": debug
        }