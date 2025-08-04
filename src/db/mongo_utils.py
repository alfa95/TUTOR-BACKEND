import os
import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from src.api.auth import hash_password

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "Users")
USER_COLLECTION_NAME = os.getenv("MONGO_USER_COLLECTION", "user")

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client[DB_NAME]
user_collection = db[USER_COLLECTION_NAME]

def create_user(email: str, name: str, password: str):
    if user_collection.find_one({"email": email}):
        return None  # User already exists
    
    user = {
        "email": email,
        "name": name,
        "password": hash_password(password),
        "goal": {
            "topic": "Polity",
            "duration_days": 14,
            "daily_target": 10
        },
        "progress": {
            "days_completed": 0,
            "sessions": [],
            "topics_covered": [],
            "last_active": None
        },
        "created_at": datetime.datetime.utcnow()
    }
    user_collection.insert_one(user)
    return user

def get_user_by_email(email: str):
    return user_collection.find_one({"email": email})

def update_user_goal(email: str, topic: str, duration_days: int, daily_target: int = 10):
    return user_collection.update_one(
        {"email": email},
        {
            "$set": {
                "goal": {
                    "topic": topic,
                    "duration_days": duration_days,
                    "daily_target": daily_target
                }
            }
        }
    )
