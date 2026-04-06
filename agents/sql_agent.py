from typing import List, Dict, Any

from langchain_openai import ChatOpenAI

from tools.db_tools import generate_sql, run_sql_query, format_sql_result


class SQLAgent:
    def __init__(self, db_path: str, openai_api_key: str):
        self.db_path = db_path
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)

    def run(self, question: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        sql_query = generate_sql(question=question, llm=self.llm)
        rows = run_sql_query(db_path=self.db_path, query=sql_query)
        answer = format_sql_result(question=question, sql_query=sql_query, rows=rows, llm=self.llm)

        return {
            "selected_agent": "SQLAgent",
            "answer": answer,
            "debug": {
                "sql_query": sql_query,
                "row_count": len(rows),
                "preview": rows[:5],
            }
        }