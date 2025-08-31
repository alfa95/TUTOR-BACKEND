"""
Learning Path API Models
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from src.services.learning_path_optimizer import LearningPath

class LearningPathRequest(BaseModel):
    """Request model for learning path optimization - with LLM option"""
    jwt_token: str = Field(..., description="JWT token for user authentication")
    llm: bool = Field(default=False, description="Activate LLM-powered features for enhanced recommendations")

# Enhanced Recommendations Models
class PersonalizedStrategy(BaseModel):
    """Model for personalized learning strategies"""
    strategy_name: str = Field(..., description="Name of the learning strategy")
    description: str = Field(..., description="Description of what this strategy involves")
    when_to_use: str = Field(..., description="When to apply this strategy")
    expected_outcome: str = Field(..., description="What this strategy will achieve")

class StudySchedule(BaseModel):
    """Model for study schedule recommendations"""
    daily_routine: str = Field(..., description="Daily study plan")
    weekly_structure: str = Field(..., description="Weekly learning schedule")
    session_lengths: str = Field(..., description="Optimal session durations")
    break_schedule: str = Field(..., description="When to take breaks")
    review_frequency: str = Field(..., description="How often to review material")

class RealWorldApplication(BaseModel):
    """Model for real-world applications of skills"""
    skill: str = Field(..., description="Skill name")
    application: str = Field(..., description="Real-world use case")
    project_idea: str = Field(..., description="Project to apply knowledge")
    career_relevance: str = Field(..., description="How this helps career")

class ProgressTracking(BaseModel):
    """Model for progress tracking recommendations"""
    milestone_system: str = Field(..., description="How to track progress")
    performance_metrics: str = Field(..., description="What to measure")
    goal_setting: str = Field(..., description="How to set realistic goals")
    motivation_system: str = Field(..., description="Rewards and incentives")

class AdaptiveLearning(BaseModel):
    """Model for adaptive learning recommendations"""
    difficulty_adjustment: str = Field(..., description="When to change difficulty")
    skill_progression: str = Field(..., description="When to move to next level")
    remedial_strategies: str = Field(..., description="How to handle struggles")
    success_indicators: str = Field(..., description="Signs of readiness for next step")

class ComplementaryResource(BaseModel):
    """Model for complementary learning resources"""
    resource_type: str = Field(..., description="Type of resource (Website/Book/Video/etc)")
    name: str = Field(..., description="Resource name")
    description: str = Field(..., description="What this resource provides")
    link: Optional[str] = Field(None, description="URL or reference")

class DifficultyProgression(BaseModel):
    """Model for difficulty progression strategies"""
    approach: str = Field(..., description="Overall approach to difficulty progression")
    polity_strategy: str = Field(..., description="Specific strategy for Polity")
    environment_strategy: str = Field(..., description="Specific strategy for Environment")
    current_affairs_strategy: str = Field(..., description="Specific strategy for Current Affairs")
    economy_strategy: str = Field(..., description="Specific strategy for Economy")

class GamificationElement(BaseModel):
    """Model for gamification elements"""
    element: str = Field(..., description="Element name")
    description: str = Field(..., description="What this element provides")

class EnhancedRecommendations(BaseModel):
    """Model for enhanced learning recommendations"""
    personalized_strategies: List[PersonalizedStrategy] = Field(default_factory=list, description="Personalized learning strategies")
    study_schedule: StudySchedule = Field(..., description="Study schedule recommendations")
    real_world_applications: List[RealWorldApplication] = Field(default_factory=list, description="Real-world applications")
    progress_tracking: ProgressTracking = Field(..., description="Progress tracking recommendations")
    adaptive_learning: AdaptiveLearning = Field(..., description="Adaptive learning recommendations")
    motivation_insights: List[str] = Field(default_factory=list, description="Motivational insights")
    complementary_resources: List[ComplementaryResource] = Field(default_factory=list, description="Complementary resources")
    difficulty_progression: DifficultyProgression = Field(..., description="Difficulty progression strategies")
    gamification_elements: List[GamificationElement] = Field(default_factory=list, description="Gamification elements")

# Milestone Models
class Milestone(BaseModel):
    """Model for learning milestones"""
    milestone_id: str = Field(..., description="Unique identifier for the milestone")
    name: str = Field(..., description="Milestone name")
    description: str = Field(..., description="What to achieve")
    success_criteria: List[str] = Field(..., description="Criteria for successful completion")
    estimated_time: int = Field(..., description="Estimated time in minutes")
    difficulty: str = Field(..., description="Difficulty level (beginner/intermediate/advanced)")
    motivation: str = Field(..., description="Why this milestone matters")
    practical_application: str = Field(..., description="How to apply knowledge")
    reward: str = Field(..., description="What user gains from completing this")
    prerequisites: List[str] = Field(default_factory=list, description="What needs to be completed first")

class LearningPathResponse(BaseModel):
    """Response model for learning path optimization"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Dict = Field(..., description="Learning path data including enhanced_recommendations and milestones")

# Additional models for specific learning path components
class Skill(BaseModel):
    """Individual skill information"""
    id: str
    name: str
    difficulty: str  # Now uses exact values: "Easy", "Medium", "Hard"
    estimated_time: int
    importance_score: float
    prerequisites: List[str]
    related_skills: List[str]
    career_relevance: List[str]
    labels: List[str] = []  # New field for skill categorization
    available_difficulties: List[str] = []  # Available difficulty levels: ["Easy", "Medium", "Hard"]
    question_count: int = 0  # Number of questions available for this skill

class SkillRecommendation(BaseModel):
    """Individual skill recommendation"""
    skill_id: str
    skill_name: str
    difficulty: str
    estimated_time: int
    importance_score: float
    prerequisites: List[str]
    why_important: str
    learning_tips: List[str]

class LearningMilestone(BaseModel):
    """Learning milestone"""
    milestone_id: str
    name: str
    skill_id: str
    position: int
    estimated_time: int
    difficulty: str
    description: str
    reward: str

class AlternativePath(BaseModel):
    """Alternative learning path"""
    path_id: str
    name: str
    description: str
    skills: List[Dict]
    total_time: int
    focus_area: str

class ProgressSummary(BaseModel):
    """User progress summary"""
    current_level: str
    completed_skills: List[str]
    in_progress_skills: List[str]
    next_milestone: str
    overall_progress_percentage: float 