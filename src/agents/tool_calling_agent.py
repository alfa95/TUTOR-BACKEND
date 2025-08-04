from src.agents.analysis_tools import fetch_sessions, aggregate_topic_performance, generate_summary, suggest_next_steps

def run_agent(email: str, day: int = None):
    sessions = fetch_sessions(email, day)
    if not sessions:
        return {"error": "No completed sessions found."}
    topic_stats = aggregate_topic_performance(sessions)
    summary = generate_summary({
        "topic_stats": topic_stats,
        "total_sessions": len(sessions),
        "total_questions": sum(len(s.get("questions", [])) for s in sessions)
    })
    suggestions = suggest_next_steps({
        "topic_stats": topic_stats,
        "total_sessions": len(sessions),
        "total_questions": sum(len(s.get("questions", [])) for s in sessions)
    })
    return {
        "topic_stats": topic_stats,
        "summary": summary,
        "suggestions": suggestions
    } 