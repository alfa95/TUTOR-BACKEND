import pytest
from datetime import datetime
from src.db.quiz_session_utils import (
    create_or_update_user,
    get_user,
    get_user_day,
    get_or_create_today_session,
    mark_quiz_completed,
    quiz_sessions_collection,
)

TEST_EMAIL = "as4195@gmail.com"

def teardown_function():
    quiz_sessions_collection.delete_many({"email": TEST_EMAIL})
    from src.db.quiz_session_utils import users_collection
    users_collection.delete_many({"email": TEST_EMAIL})

def test_user_creation_and_retrieval():
    user = create_or_update_user(TEST_EMAIL, "Anurag", "Polity", 7)
    assert user["email"] == TEST_EMAIL

    fetched = get_user(TEST_EMAIL)
    assert fetched is not None
    assert fetched["goal"]["topic"] == "Polity"

def test_get_user_day_zero():
    user = get_user(TEST_EMAIL)
    day = get_user_day(user)
    assert day == 0

def test_get_or_create_today_session():
    session = get_or_create_today_session(TEST_EMAIL)
    assert session["email"] == TEST_EMAIL
    assert session["day"] == 0
    assert session["topic"] == "Polity"

def test_mark_quiz_completed():
    session = get_or_create_today_session(TEST_EMAIL)
    mark_quiz_completed(TEST_EMAIL, session["day"])
    updated = quiz_sessions_collection.find_one({"email": TEST_EMAIL, "day": session["day"]})
    assert updated["completed"] is True
    assert "completed_at" in updated
