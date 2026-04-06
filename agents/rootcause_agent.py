from typing import List, Dict, Any

from langchain_openai import ChatOpenAI

from tools.analytics_tools import build_root_cause_prompt


class RootCauseAgent:
    def __init__(self, db_path: str, openai_api_key: str):
        self.db_path = db_path
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_api_key)

    def run(self, question: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        prompt, diagnostics = build_root_cause_prompt(question=question, db_path=self.db_path)
        answer = self.llm.invoke(prompt).content

        return {
            "selected_agent": "RootCauseAgent",
            "answer": answer,
            "debug": diagnostics
        }