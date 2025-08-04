from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from src.vector_store.qdrant_utils import search_similar_questions
from src.llm.embedder import embed_texts
from src.llm.model_router import route_llm


# Step 1: Define state structure
class RAGState(TypedDict, total=False):
    query: str
    embedding: List[float]
    context: List[dict]
    response: dict  # Structured response
    model_type: str  # e.g., "gemini", "hf", etc.
    model_name: str  # Optional override for model selection
    use_llm: bool = False  # Whether to use LLM for explanation


# Step 2: Embed query
def embed_query_node(state: RAGState) -> RAGState:
    embedding = embed_texts([state["query"]])[0]
    return {**state, "embedding": embedding}


# Step 3: Search Qdrant
def search_qdrant_node(state: RAGState) -> RAGState:
    hits = search_similar_questions(state["query"], top_k=5)

    if not hits:
        return {
            **state,
            "context": [],
            "response": {
                "text": "Sorry, I couldn't find relevant content to answer this question.",
                "model": None,
                "metadata": {}
            }
        }
    return {**state, "context": hits}


# Step 4: Generate answer with LLM
def generate_response_node(state: RAGState) -> RAGState:
    if not state.get("context"):
        return state  # Can't generate anything without context

    response_payload = {
        "questions": state["context"],
        "model": None,
        "metadata": {}
    }
    if state.get("use_llm"):
        context_text = "\n".join([f"- {hit['question']}" for hit in state["context"]])
        prompt = f"""You are a tutor. Based on the following context questions, generate a summary explanation or thematic insight for the user:
{context_text}
"""
        model_type = state.get("model_type", "gemini")
        model_name = state.get("model_name")
        llm = route_llm(model_type=model_type, model_name=model_name)
        if not llm:
            print("⚠️ LLM could not be initialized. Skipping explanation.")
        else:
            answer_msg = llm.invoke(prompt)
            response_payload["model"] = model_type
            response_payload["metadata"] = getattr(answer_msg, "response_metadata", {})
            response_payload["explanation"] = answer_msg.content
    return {**state, "response": response_payload}



# Step 5: Build the LangGraph
def build_rag_graph():
    builder = StateGraph(RAGState)

    builder.add_node("embed_query", embed_query_node)
    builder.add_node("search_qdrant", search_qdrant_node)
    builder.add_node("generate_response", generate_response_node)

    builder.set_entry_point("embed_query")
    builder.add_edge("embed_query", "search_qdrant")
    builder.add_edge("search_qdrant", "generate_response")
    builder.add_edge("generate_response", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_rag_graph()
    inputs = {
        "query": "What is the purpose of Chandrayaan-3?",
        "model_type": "gemini",
        "model_name": "gemini-1.5-flash"
    }
    result = graph.invoke(inputs)
    print("🔍 Final Response:\n", result.get("response", {}).get("text"))
