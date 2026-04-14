from typing import TypedDict, List, Dict, Any, Optional
import re
import time

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from agents.sql_agent import SQLAgent
from agents.rag_agent import RAGAgent
from agents.rootcause_agent import RootCauseAgent
from agents.recommendation_agent import RecommendationAgent


class GraphState(TypedDict, total=False):
    question: str
    history: List[Dict[str, str]]
    route: str
    answer: str
    selected_agent: str
    debug: Dict[str, Any]
    rootcause_answer: str
    rootcause_debug: Dict[str, Any]


class SupervisorAgent:
    def __init__(
        self,
        db_path: str,
        qdrant_url: Optional[str],
        qdrant_api_key: Optional[str],
        openai_api_key: str,
        collection_name: str = "olist_docs",
    ):
        self.router_llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=openai_api_key
        )

        self.sql_agent = SQLAgent(db_path=db_path, openai_api_key=openai_api_key)
        self.rag_agent = RAGAgent(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            openai_api_key=openai_api_key,
            collection_name=collection_name
        )
        self.rootcause_agent = RootCauseAgent(db_path=db_path, openai_api_key=openai_api_key)
        self.recommendation_agent = RecommendationAgent(
            db_path=db_path,
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            openai_api_key=openai_api_key,
            collection_name=collection_name
        )

        self.graph = self._build_graph()

    def _heuristic_route(self, question: str) -> Optional[str]:
        q = question.lower()

        review_semantic_patterns = [
            r"\breview\b",
            r"\breviews\b",
            r"\bcomplaint\b",
            r"\bcomplaints\b",
            r"\bfeedback\b",
            r"\bsentiment\b",
            r"\bsemantic\b",
            r"\bnarrative\b",
            r"customer(s)? say",
            r"what are customers saying",
            r"common complaint",
            r"common complaints",
            r"translate this review",
            r"summari[sz]e .*review",
            r"theme[s]? in .*review",
        ]
        if any(re.search(pattern, q) for pattern in review_semantic_patterns):
            return "rag"

        recommendation_keywords = [
            "recommend", "recommendation", "action plan", "what should",
            "how can we improve", "what should management do", "prioritize"
        ]
        if any(k in q for k in recommendation_keywords):
            return "recommendation"

        rootcause_keywords = [
            "root cause", "why", "driver", "drivers", "reason", "reasons",
            "investigate", "diagnose"
        ]
        if any(k in q for k in rootcause_keywords):
            return "rootcause"

        return None

    def _route_question(self, state: GraphState) -> GraphState:
        start = time.perf_counter()

        question = state["question"]
        history = state.get("history", [])

        history_text = "\n".join(
            [f'{m.get("role", "")}: {m.get("content", "")}' for m in history[-10:]]
        )

        heuristic_route = self._heuristic_route(question)

        prompt = f"""
You are a supervisor for a multi-agent e-commerce analytics system.

Choose exactly one route from:
- sql
- rag
- rootcause
- recommendation

Rules:
- sql: counts, KPIs, totals, top/bottom, trends, comparisons, trends over time, structured aggregations from tables
- rag: any review-semantics or narrative request, including customer complaints, customer feedback, review sentiment, common themes in reviews, translation of review text, semantic similarity across reviews, and any schema/definition/glossary question
- rootcause: why, diagnose, reasons, drivers, investigate, explain likely causes using structured analytics
- recommendation: actions, action plan, strategy, improve, optimize, what should management do

Important:
- If the user asks about what customers said in reviews, complaints, sentiment, review themes, or semantic patterns, choose rag.
- Do not send review-semantic questions to sql just because they mention scores or deliveries.

Return only one word.

Conversation History:
{history_text}

Question:
{question}
"""
        response = self.router_llm.invoke(prompt)
        route = heuristic_route or response.content.strip().lower()
        if route not in {"sql", "rag", "rootcause", "recommendation"}:
            route = "sql"

        usage = getattr(response, "response_metadata", {}).get("token_usage", {}) or {}
        elapsed = time.perf_counter() - start

        return {
            **state,
            "route": route,
            "debug": {
                "supervisor_telemetry": {
                    "routing": {
                        "selected_route": route,
                        "routing_latency_sec": round(elapsed, 4),
                    },
                    "tokens": {
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    "quality": {
                        "status": "success",
                        "route_valid": route in {"sql", "rag", "rootcause", "recommendation"}
                    }
                }
            }
        }

    def _route_edges(self, state: GraphState) -> str:
        return state["route"]

    def _sql_node(self, state: GraphState) -> GraphState:
        result = self.sql_agent.run(state["question"], state.get("history", []))
        merged_debug = {**state.get("debug", {}), **result.get("debug", {})}
        return {
            **state,
            "answer": result["answer"],
            "selected_agent": "SQLAgent",
            "debug": merged_debug
        }

    def _rag_node(self, state: GraphState) -> GraphState:
        result = self.rag_agent.run(state["question"], state.get("history", []))
        merged_debug = {**state.get("debug", {}), **result.get("debug", {})}
        return {
            **state,
            "answer": result["answer"],
            "selected_agent": "RAGAgent",
            "debug": merged_debug
        }

    def _rootcause_node(self, state: GraphState) -> GraphState:
        result = self.rootcause_agent.run(state["question"], state.get("history", []))
        merged_debug = {**state.get("debug", {}), **result.get("debug", {})}
        return {
            **state,
            "rootcause_answer": result["answer"],
            "rootcause_debug": result.get("debug", {}),
            "selected_agent": "RootCauseAgent",
            "debug": merged_debug
        }

    def _recommendation_node(self, state: GraphState) -> GraphState:
        base_question = state["question"]

        if state.get("rootcause_answer"):
            enriched_question = f"""
User question:
{base_question}

Root cause findings:
{state["rootcause_answer"]}

Based on the root-cause findings above, provide prioritized recommendations.
"""
        else:
            enriched_question = base_question

        result = self.recommendation_agent.run(
            enriched_question,
            state.get("history", [])
        )

        merged_debug = {**state.get("debug", {}), **result.get("debug", {})}

        if state.get("rootcause_debug"):
            merged_debug["rootcause_chain"] = state["rootcause_debug"]

        return {
            **state,
            "answer": result["answer"],
            "selected_agent": "RecommendationAgent [uses SQL + RAG]"
            if not state.get("rootcause_answer")
            else "RootCauseAgent [uses SQL] -> RecommendationAgent [uses SQL + RAG]",
            "debug": merged_debug
        }

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("router", self._route_question)
        workflow.add_node("sql", self._sql_node)
        workflow.add_node("rag", self._rag_node)
        workflow.add_node("rootcause", self._rootcause_node)
        workflow.add_node("recommendation", self._recommendation_node)

        workflow.set_entry_point("router")

        workflow.add_conditional_edges(
            "router",
            self._route_edges,
            {
                "sql": "sql",
                "rag": "rag",
                "rootcause": "rootcause",
                "recommendation": "recommendation",
            }
        )

        workflow.add_edge("sql", END)
        workflow.add_edge("rag", END)
        workflow.add_edge("recommendation", END)
        workflow.add_edge("rootcause", "recommendation")

        return workflow.compile()

    def run(self, question: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        total_start = time.perf_counter()

        state: GraphState = {
            "question": question,
            "history": history or [],
        }
        result = self.graph.invoke(state)

        total_elapsed = time.perf_counter() - total_start
        debug = result.get("debug", {}) or {}

        supervisor_debug = debug.get("supervisor_telemetry", {})
        supervisor_debug["request"] = {
            "total_request_latency_sec": round(total_elapsed, 4)
        }
        debug["supervisor_telemetry"] = supervisor_debug

        return {
            "answer": result.get("answer", "No answer generated."),
            "selected_agent": result.get("selected_agent", result.get("route", "unknown")),
            "debug": debug
        }