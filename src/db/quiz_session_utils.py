from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "Users")
COLLECTION_NAME = os.getenv("MONGO_QUIZ_COLLECTION", "quiz_sessions")
USER_COLLECTION_NAME = os.getenv("MONGO_USER_COLLECTION", "user")


client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client[DB_NAME]
users_collection = db[USER_COLLECTION_NAME]
quiz_sessions_collection = db[COLLECTION_NAME]

def get_today_date():
    return datetime.utcnow().date()

def get_user(email: str):
    return users_collection.find_one({"email": email})

def create_or_update_user(email: str, name: str, goal_topic: str, duration_days: int):
    user = get_user(email)
    if not user:
        user = {
            "email": email,
            "name": name,
            "goal": {
                "topic": goal_topic,
                "duration_days": duration_days,
                "daily_target": 10,
                "start_date": get_today_date().isoformat()
            },
            "created_at": datetime.utcnow()
        }
        users_collection.insert_one(user)
    return user

def get_user_day(user):
    start_date = datetime.fromisoformat(user["goal"]["start_date"]).date()
    today = get_today_date()
    return (today - start_date).days

def quiz_session_exists(email: str, day: int) -> bool:
    return quiz_sessions_collection.find_one({"email": email, "day": day}) is not None

def create_quiz_session(email: str, day: int, topic: str, num_questions: int):
    session = {
        "email": email,
        "day": day,
        "topic": topic,
        "questions_served": [],  # can be filled later with UUIDs or questions
        "completed": False,
        "created_at": datetime.utcnow()
    }
    quiz_sessions_collection.insert_one(session)
    return session

def get_or_create_today_session(email: str):
    user = get_user(email)
    if not user:
        raise ValueError("User does not exist")

    day = get_user_day(user)
    topic = user["goal"]["topic"]
    
    existing = quiz_sessions_collection.find_one({"email": email, "day": day})
    if existing:
        return existing

    return create_quiz_session(email=email, day=day, topic=topic, num_questions=user["goal"].get("daily_target", 10))

def mark_quiz_completed(email: str, day: int):
    quiz_sessions_collection.update_one(
        {"email": email, "day": day},
        {"$set": {"completed": True, "completed_at": datetime.utcnow()}}
    )
