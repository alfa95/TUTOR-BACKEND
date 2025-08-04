from src.db.quiz_session_utils import quiz_sessions_collection
from collections import defaultdict
from src.llm.model_router import route_llm

def fetch_sessions(email: str, day: int = None):
    if day is not None:
        sessions = list(quiz_sessions_collection.find({"email": email, "day": day, "completed": True}))
    else:
        sessions = list(quiz_sessions_collection.find({"email": email, "completed": True}))
    return sessions

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
    return dict(topic_stats)

def generate_summary(performance_data):
    llm = route_llm(model_type="gemini", model_name="gemini-1.5-flash")
    prompt = (
        "You are an educational analytics assistant. Given the following quiz performance data, "
        "generate a detailed, human-readable summary and actionable feedback for the user.\n"
        f"Performance Data: {performance_data}\n"
        "Be concise, highlight strengths and weaknesses, and suggest next steps."
    )
    response = llm.invoke(prompt)
    return getattr(response, "content", str(response))

def suggest_next_steps(performance_data):
    llm = route_llm(model_type="gemini", model_name="gemini-1.5-flash")
    prompt = (
        "Given the following quiz performance data, suggest concrete next steps for the user to improve their learning outcomes.\n"
        f"Performance Data: {performance_data}\n"
        "Be specific and actionable."
    )
    response = llm.invoke(prompt)
    return getattr(response, "content", str(response)) 