"""
Quiz Models - Data structures for quiz functionality
"""
from pydantic import BaseModel
from typing import List, Dict, Optional

class AdaptiveQuizRequest(BaseModel):
    jwt_token: str
    num_questions: int = 10
    topics: Optional[List[str]] = None  # Optional: specific topics to focus on

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: str
    topic: str
    difficulty: str
    explanation: Optional[str] = None

class AdaptiveQuizResponse(BaseModel):
    user_id: str
    progress_summary: Dict
    recommended_questions: List[QuizQuestion]
    quiz_strategy: str

class UserProgressSummary(BaseModel):
    strategy: str
    overall_accuracy: float
    total_attempts: int
    total_correct: int
    topic_performance: Dict
    topics: List[str]
    difficulties: List[str]

class VectorDBFilter(BaseModel):
    should: List[Dict] 