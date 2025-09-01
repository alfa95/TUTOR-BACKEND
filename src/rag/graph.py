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
    enable_reranking: bool = False  # Whether to rerank search results
    reranking_strategy: str = "semantic_relevance"  # Reranking strategy


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

# Step 3.5: Rerank search results (optional)
def rerank_results_node(state: RAGState) -> RAGState:
    if not state.get("enable_reranking") or not state.get("context"):
        return state
    
    try:
        from src.services.reranking_service import reranking_service
        
        # Convert context to reranking format
        search_results = []
        for i, hit in enumerate(state["context"]):
            search_results.append({
                "title": hit.get("question", f"Result {i+1}"),
                "link": hit.get("source", f"#result-{i+1}"),
                "snippet": hit.get("answer", hit.get("question", "")),
                "position": i + 1
            })
        
        print(f"🔍 Converting {len(search_results)} results for reranking")
        
        # Apply reranking
        reranked_results = reranking_service.rerank_results(
            state["query"],
            search_results,
            state.get("reranking_strategy", "semantic_relevance")
        )
        
        print(f"🔍 Reranking returned {len(reranked_results)} results")
        
        # Convert back to original format and update context
        reranked_context = []
        for reranked in reranked_results:
            # Find original hit by position (using index-based matching)
            original_position = reranked["position"]
            if 1 <= original_position <= len(state["context"]):
                original_hit = state["context"][original_position - 1]  # Convert to 0-based index
                
                # Add reranking metadata
                reranked_hit = {**original_hit}
                reranked_hit["relevance_score"] = reranked["relevance_score"]
                reranked_hit["rerank_position"] = reranked["rerank_position"]
                reranked_context.append(reranked_hit)
                print(f"✅ Mapped position {original_position} to result: {reranked_hit.get('question', 'No title')[:30]}...")
            else:
                print(f"⚠️ Invalid position {original_position} in reranked results")
        
        # Sort by rerank position
        reranked_context.sort(key=lambda x: x.get("rerank_position", 0))
        
        print(f"✅ Reranked {len(reranked_context)} results for query: {state['query']}")
        
        # Ensure we always return the original context if reranking fails
        if not reranked_context:
            print("⚠️ Reranking produced no results, returning original context")
            # Add fallback metadata to original context
            fallback_context = []
            for i, hit in enumerate(state["context"]):
                fallback_hit = {**hit}
                fallback_hit["relevance_score"] = max(0.1, 1.0 - (i * 0.1))
                fallback_hit["rerank_position"] = i + 1
                fallback_context.append(fallback_hit)
            
            print(f"✅ Applied fallback scoring to {len(fallback_context)} results")
            return {**state, "context": fallback_context}
            
        return {**state, "context": reranked_context}
        
    except Exception as e:
        print(f"⚠️ Reranking failed, using original results: {e}")
        return state


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
    builder.add_node("rerank_results", rerank_results_node)
    builder.add_node("generate_response", generate_response_node)

    builder.set_entry_point("embed_query")
    builder.add_edge("embed_query", "search_qdrant")
    builder.add_edge("search_qdrant", "rerank_results")
    builder.add_edge("rerank_results", "generate_response")
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
