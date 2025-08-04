from src.db.quiz_session_utils import quiz_sessions_collection
from collections import defaultdict
from src.llm.model_router import route_llm

def aggregate_topic_performance(sessions):
    topic_stats = defaultdict(lambda: {"total": 0, "correct": 0})
    for session in sessions:
        for q in session.get("questions", []):
            topic = q.get("topic")
            if topic:
                topic_stats[topic]["total"] += 1
                if q.get("is_correct"):
                    topic_stats[topic]["correct"] += 1
    for topic, stats in topic_stats.items():
        stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] else 0
    return topic_stats

def summarize_performance(summary_input):
    llm = route_llm(model_type="gemini", model_name="gemini-1.5-flash")
    prompt = (
        "You are an educational analytics assistant. Given the following quiz performance data, "
        "generate a detailed, human-readable summary and actionable feedback for the user.\n"
        f"Performance Data: {summary_input}\n"
        "Be concise, highlight strengths and weaknesses, and suggest next steps."
    )
    response = llm.invoke(prompt)
    return getattr(response, "content", str(response))

def analyze_user(email: str, day: int = None):
    if day is not None:
        sessions = list(quiz_sessions_collection.find({"email": email, "day": day, "completed": True}))
        analysis_type = "session"
    else:
        sessions = list(quiz_sessions_collection.find({"email": email, "completed": True}))
        analysis_type = "overall"
    if not sessions:
        return {"error": "No completed sessions found."}
    topic_stats = aggregate_topic_performance(sessions)
    summary_input = {
        "type": analysis_type,
        "topic_stats": topic_stats,
        "total_sessions": len(sessions),
        "total_questions": sum(len(s.get("questions", [])) for s in sessions)
    }
    if analysis_type == "session":
        summary_input["score"] = sessions[0].get("score", 0)
    summary = summarize_performance(summary_input)
    return {"topic_stats": topic_stats, "summary": summary} 