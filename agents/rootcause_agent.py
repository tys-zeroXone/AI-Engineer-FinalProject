from typing import List, Dict, Any
import time

from langchain_openai import ChatOpenAI

from tools.analytics_tools import build_root_cause_prompt


class RootCauseAgent:
    def __init__(self, db_path: str, openai_api_key: str):
        self.db_path = db_path
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_api_key)

    def run(self, question: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        agent_start = time.perf_counter()

        prompt, diagnostics, diagnostics_telemetry = build_root_cause_prompt(
            question=question,
            db_path=self.db_path
        )

        llm_start = time.perf_counter()
        response = self.llm.invoke(prompt)
        llm_elapsed = time.perf_counter() - llm_start

        usage = getattr(response, "response_metadata", {}).get("token_usage", {}) or {}
        total_elapsed = time.perf_counter() - agent_start

        return {
            "selected_agent": "RootCauseAgent",
            "answer": response.content,
            "debug": {
                "agent_telemetry": {
                    "agent_name": "RootCauseAgent",
                    "timing": {
                        "total_latency_sec": round(total_elapsed, 4),
                        "rootcause_generation_sec": round(llm_elapsed, 4),
                        **diagnostics_telemetry.get("timing", {})
                    },
                    "tokens": {
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    "diagnostics": diagnostics,
                    "quality": {
                        **diagnostics_telemetry.get("quality", {}),
                        "accuracy_note": "Execution-quality telemetry only. Root-cause correctness remains hypothesis-based unless benchmarked."
                    }
                }
            }
        }