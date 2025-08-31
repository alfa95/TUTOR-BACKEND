from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from src.agents.internet_search_tools import search_internet, search_with_context
from src.llm.model_router import route_llm

# Define state structure for internet search
class InternetSearchState(TypedDict, total=False):
    query: str
    context: str
    search_results: List[dict]
    response: dict
    model_type: str
    model_name: str
    use_llm: bool = False

# Step 1: Process the query
def process_query_node(state: InternetSearchState) -> InternetSearchState:
    """Process and validate the search query"""
    query = state.get("query", "").strip()
    if not query:
        return {**state, "error": "Query cannot be empty"}
    
    return {**state, "query": query}

# Step 2: Perform internet search
def search_node(state: InternetSearchState) -> InternetSearchState:
    """Perform internet search using SerperDev"""
    query = state.get("query", "")
    context = state.get("context", "")
    
    try:
        results = search_internet(query, num_results=4)
        return {**state, "search_results": results}
    except Exception as e:
        return {**state, "error": f"Search failed: {str(e)}"}

# Step 3: Generate response (optional LLM enhancement)
def generate_response_node(state: InternetSearchState) -> InternetSearchState:
    """Generate final response, optionally using LLM for enhancement"""
    search_results = state.get("search_results", [])
    
    if not search_results:
        return {**state, "response": {"error": "No search results found"}}
    
    # Check if any results have errors
    error_results = [r for r in search_results if "error" in r]
    if error_results:
        return {**state, "response": {"error": "Search encountered errors", "details": error_results}}
    
    response_payload = {
        "query": state.get("query", ""),
        "results": search_results,
        "total_results": len(search_results),
        "timestamp": None
    }
    
    # Optional LLM enhancement
    if state.get("use_llm", False):
        try:
            model_type = state.get("model_type", "gemini")
            model_name = state.get("model_name", "gemini-1.5-flash")
            llm = route_llm(model_type=model_type, model_name=model_name)
            
            if llm:
                # Create a summary of the search results
                results_text = "\n".join([
                    f"{i+1}. {result['title']}\n   {result['snippet']}\n   URL: {result['link']}\n"
                    for i, result in enumerate(search_results)
                ])
                
                prompt = f"""Based on the following internet search results for the query "{state.get('query', '')}", 
                provide a concise summary and key insights:

                {results_text}
                
                Please provide:
                1. A brief summary of what was found
                2. Key insights or patterns
                3. Any notable sources or authorities
                """
                
                llm_response = llm.invoke(prompt)
                response_payload["llm_summary"] = getattr(llm_response, "content", str(llm_response))
                response_payload["model_used"] = f"{model_type}:{model_name}"
        except Exception as e:
            print(f"⚠️ LLM enhancement failed: {e}")
            response_payload["llm_error"] = str(e)
    
    return {**state, "response": response_payload}

# Build the LangGraph for internet search
def build_internet_search_graph():
    """Build the LangGraph for internet search workflow"""
    builder = StateGraph(InternetSearchState)
    
    # Add nodes
    builder.add_node("process_query", process_query_node)
    builder.add_node("search", search_node)
    builder.add_node("generate_response", generate_response_node)
    
    # Set entry point
    builder.set_entry_point("process_query")
    
    # Add edges
    builder.add_edge("process_query", "search")
    builder.add_edge("search", "generate_response")
    builder.add_edge("generate_response", END)
    
    return builder.compile()

# Convenience function to run the graph
def run_internet_search(query: str, use_llm: bool = False):
    """
    Run internet search using LangGraph
    
    Args:
        query (str): Search query
        use_llm (bool): Whether to use LLM for response enhancement
    
    Returns:
        dict: Search results and optional LLM enhancement
    """
    try:
        graph = build_internet_search_graph()
        
        inputs = {
            "query": query,
            "context": "",  # No context needed for simple queries
            "use_llm": use_llm,
            "model_type": "gemini",  # Default to Gemini
            "model_name": "gemini-1.5-flash"  # Default model
        }
        
        result = graph.invoke(inputs)
        return result.get("response", {"error": "No response generated"})
        
    except Exception as e:
        print(f"❌ Error running internet search graph: {e}")
        return {"error": f"Graph execution failed: {str(e)}"}

# Create a global instance for easy access
internet_search_graph = build_internet_search_graph() 