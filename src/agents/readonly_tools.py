import logging
from src.db.quiz_session_utils import quiz_sessions_collection
from collections import defaultdict

def fetch_sessions(email: str, limit: int = None, sort_by: str = "session_date", order: str = "desc"):
    logging.info(f"[TOOL CALL] fetch_sessions called with: email={email}, limit={limit}, sort_by={sort_by}, order={order}")
    query = {"user_email": email}
    logging.info(f"[MONGO QUERY] quiz_sessions_collection.find({query})")
    cursor = quiz_sessions_collection.find(query)
    if sort_by:
        cursor = cursor.sort(sort_by, -1 if order == "desc" else 1)
    if limit:
        cursor = cursor.limit(limit)
    result = list(cursor)
    logging.info(f"[RESULT] {len(result)} sessions fetched: {result[:2]}..." if result else "[RESULT] No sessions fetched.")
    return result

def filter_sessions_by_score(sessions, min_score: int = None, max_score: int = None):
    logging.info(f"[TOOL CALL] filter_sessions_by_score called with: min_score={min_score}, max_score={max_score}")
    filtered = []
    for session in sessions:
        if min_score is not None and session["score"] < min_score:
            continue
        if max_score is not None and session["score"] > max_score:
            continue
        filtered.append(session)
    logging.info(f"[RESULT] {len(filtered)} sessions after filtering by score: {filtered[:2]}..." if filtered else "[RESULT] No sessions after filtering.")
    return filtered

def aggregate_topic_performance(sessions):
    logging.info(f"[TOOL CALL] aggregate_topic_performance called with {len(sessions)} sessions")
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
    logging.info(f"[RESULT] Topic stats: {dict(topic_stats)}")
    return dict(topic_stats) 