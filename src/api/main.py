from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Query, Depends, status
from pydantic import BaseModel
from src.rag.graph import build_rag_graph
from src.db.quiz_session_utils import (
    get_or_create_today_session,
    mark_quiz_completed
)
from src.services.adaptive_quiz_service import adaptive_quiz_service
from src.models.quiz_models import AdaptiveQuizRequest, AdaptiveQuizResponse
from typing import List, Dict
from datetime import datetime
from collections import defaultdict
from src.agents.analysis_agent import analyze_user
from src.agents.tool_calling_agent import run_agent
from src.agents.langgraph_agent import run_nl_query
from src.agents.langgraph_openai_agent import run_openai_query
from src.api.auth import restricted_api_key

app = FastAPI()
rag_graph = build_rag_graph()

@app.get("/")
async def root():
    return {
        "message": "Tutor Backend API",
        "status": "running",
        "version": "1.0.0"
    }

class QueryRequest(BaseModel):
    query: str
    use_llm: bool = False

class QueryResponse(BaseModel):
    response: dict

class QuizSessionRequest(BaseModel):
    email: str

class MarkCompletedRequest(BaseModel):
    email: str
    day: int

class SubmitQuizRequest(BaseModel):
    email: str
    day_number: int
    answers: List[Dict]  # Each dict: {question_id, user_answer}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    try:
        inputs = request.dict()
        inputs["model_type"] = "gemini"
        inputs["model_name"] = "gemini-1.5-flash"
        result = rag_graph.invoke(inputs)
        return {"response": result.get("response", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quiz-session/today")
def get_today_quiz_session(request: QuizSessionRequest):
    session = get_or_create_today_session(request.email)
    return {"session": session}

@app.post("/quiz-session/mark-completed")
def mark_quiz_completed_endpoint(request: MarkCompletedRequest):
    mark_quiz_completed(request.email, request.day)
    return {"status": "completed"}

@app.post("/quiz-session/submit")
def submit_quiz_answers(request: SubmitQuizRequest):
    # Fetch the session
    session = quiz_sessions_collection.find_one({"email": request.email, "day": request.day_number})
    if not session:
        raise HTTPException(status_code=404, detail="Quiz session not found")

    # Update questions with user answers and correctness
    updated_questions = []
    correct_count = 0
    for q in session["questions"]:
        user_answer = next((a["user_answer"] for a in request.answers if a["question_id"] == q["question_id"]), None)
        is_correct = user_answer == q["correct_answer"]
        if is_correct:
            correct_count += 1
        updated_questions.append({
            **q,
            "user_answer": user_answer,
            "is_correct": is_correct
        })

    # Update session in DB
    quiz_sessions_collection.update_one(
        {"email": request.email, "day": request.day_number},
        {"$set": {
            "questions": updated_questions,
            "score": correct_count,
            "total_questions": len(updated_questions),
            "completed": True,
            "completed_at": datetime.utcnow()
        }}
    )
    # Return updated session
    updated_session = quiz_sessions_collection.find_one({"email": request.email, "day": request.day_number})
    return {"session": updated_session}

@app.get("/user/analyze")
def analyze_user_tool(email: str = Query(...), day: int = Query(None)):
    result = analyze_user(email, day)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/user/in-depth-analysis")
def in_depth_analysis(email: str = Query(...), day: int = Query(None)):
    result = run_agent(email, day)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/user/query-gpt")
def query_gpt_endpoint(email: str, prompt: str, api_key: str = Depends(restricted_api_key)):
    result = run_nl_query(prompt, context={"email": email})
    return {"result": result}

@app.post("/user/query-openai")
def query_openai_endpoint(email: str, prompt: str, api_key: str = Depends(restricted_api_key)):
    result = run_openai_query(prompt, email)
    return {"result": result}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# === Adaptive Quiz Questions Endpoint ===

@app.post("/quiz/adaptive-questions", response_model=AdaptiveQuizResponse)
def get_adaptive_quiz_questions(request: AdaptiveQuizRequest):
    """
    Get adaptive quiz questions based on user's topic progress
    """
    try:
        # Use the service to handle all the logic (user_id extracted from JWT)
        result = adaptive_quiz_service.get_adaptive_quiz_questions(
            jwt_token=request.jwt_token,
            num_questions=10,
            topics=request.topics
        )
        
        return AdaptiveQuizResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in adaptive quiz endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate adaptive quiz: {str(e)}") 
