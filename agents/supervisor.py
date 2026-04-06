from typing import TypedDict, List, Dict, Any, Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
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

    def _route_question(self, state: GraphState) -> GraphState:
        question = state["question"]
        history = state.get("history", [])

        history_text = "\n".join(
            [f'{m.get("role", "")}: {m.get("content", "")}' for m in history[-10:]]
        )

        prompt = f"""
You are a supervisor for a multi-agent e-commerce analytics system.

Choose exactly one route from:
- sql
- rag
- rootcause
- recommendation

Rules:
- sql: counts, KPIs, totals, top/bottom, trends, comparisons
- rag: explain metrics, schema, glossary, join logic, dataset definitions
- rootcause: why, diagnose, reasons, drivers, investigate
- recommendation: actions, action plan, strategy, improve, optimize

Return only one word.

Conversation History:
{history_text}

Question:
{question}
"""
        route = self.router_llm.invoke(prompt).content.strip().lower()
        if route not in {"sql", "rag", "rootcause", "recommendation"}:
            route = "sql"

        return {**state, "route": route}

    def _route_edges(self, state: GraphState) -> str:
        return state["route"]

    def _sql_node(self, state: GraphState) -> GraphState:
        result = self.sql_agent.run(state["question"], state.get("history", []))
        return {
            **state,
            "answer": result["answer"],
            "selected_agent": "SQLAgent",
            "debug": result.get("debug", {})
        }

    def _rag_node(self, state: GraphState) -> GraphState:
        result = self.rag_agent.run(state["question"], state.get("history", []))
        return {
            **state,
            "answer": result["answer"],
            "selected_agent": "RAGAgent",
            "debug": result.get("debug", {})
        }

    def _rootcause_node(self, state: GraphState) -> GraphState:
        result = self.rootcause_agent.run(state["question"], state.get("history", []))
        return {
            **state,
            "rootcause_answer": result["answer"],
            "rootcause_debug": result.get("debug", {}),
            "selected_agent": "RootCauseAgent"
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

        combined_debug = result.get("debug", {})
        if state.get("rootcause_debug"):
            combined_debug["rootcause_debug"] = state["rootcause_debug"]

        return {
            **state,
            "answer": result["answer"],
            "selected_agent": "RecommendationAgent"
                              if not state.get("rootcause_answer")
                              else "RootCauseAgent -> RecommendationAgent",
            "debug": combined_debug
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
        state: GraphState = {
            "question": question,
            "history": history or [],
        }
        result = self.graph.invoke(state)

        return {
            "answer": result.get("answer", "No answer generated."),
            "selected_agent": result.get("selected_agent", result.get("route", "unknown")),
            "debug": result.get("debug", {})
        }