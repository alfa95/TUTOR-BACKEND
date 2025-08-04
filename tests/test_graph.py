from src.rag.graph import build_rag_graph

def test_rag_graph_without_llm():
    graph = build_rag_graph()
    state = {
        "query": "Give me questions on Wildlife Sanctuary?",
    }

    result = graph.invoke(state)

    assert "response" in result
    assert "questions" in result["response"]
    assert isinstance(result["response"]["questions"], list)
    assert len(result["response"]["questions"]) > 0
    print("\n📘 Non-LLM Questions:\n", result["response"]["questions"])


def test_rag_graph_with_llm():
    graph = build_rag_graph()
    state = {
        "query": "Give me questions on Wildlife Sanctuary?",
        "model_type": "gemini",
        "model_name": "gemini-1.5-flash",
        "use_llm": True
    }

    result = graph.invoke(state)

    assert "response" in result
    assert "questions" in result["response"]

    if state.get("use_llm"):
        assert "explanation" in result["response"]
        assert isinstance(result["response"]["explanation"], str)
        assert len(result["response"]["explanation"]) > 0
