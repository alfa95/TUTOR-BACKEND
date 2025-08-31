from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.rag.graph import build_rag_graph

from src.services.adaptive_quiz_service import adaptive_quiz_service
from src.models.quiz_models import AdaptiveQuizRequest, AdaptiveQuizResponse
from src.services.learning_path_optimizer import learning_path_optimizer
from src.models.learning_path_models import LearningPathRequest, LearningPathResponse
from src.services.gemini_learning_enhancer import gemini_enhancer


from src.agents.internet_search_agent import run_internet_search


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",      # Your frontend dev server
        "http://localhost:3000",      # Alternative frontend port
        "http://localhost:5173",      # Vite default port
        "http://localhost:4173",      # Your production domain
        "https://skillquest.pages.dev"  # SkillQuest frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "accept", "apikey", "accept-profile"]
)

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





@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# === Quiz Detail Endpoint (Internet Search) ===

class QuizDetailRequest(BaseModel):
    query: str
    use_llm: bool = False

@app.post("/quiz-detail")
def get_quiz_detail(request: QuizDetailRequest):
    """
    Get internet search results for quiz questions using LangGraph and SerperDev
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = run_internet_search(
            query=request.query.strip(),
            use_llm=request.use_llm
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in quiz-detail endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz details: {str(e)}")

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
            num_questions=request.num_questions,
            topic_requests=request.topic_requests
        )
        
        return AdaptiveQuizResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in adaptive quiz endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate adaptive quiz: {str(e)}") 

@app.post("/learning-path/dashboard", response_model=LearningPathResponse)
async def get_learning_dashboard(
    request: LearningPathRequest
    # Single endpoint - with LLM option!
):
    """
    Get comprehensive learning dashboard - with optional LLM enhancement!
    """
    try:
        # Extract user_id from JWT token
        from src.api.jwt_utils import get_user_from_jwt
        
        user_info = get_user_from_jwt(request.jwt_token)
        user_id = user_info.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=401, 
                detail="Invalid JWT token: user_id not found"
            )
        
        # Get user's current progress from Supabase
        from src.db.supabase_utils import get_user_topic_progress
        user_progress = get_user_topic_progress(user_id)
        
        if not user_progress:
            # New user - create empty progress structure
            current_progress = {
                "strategy": "cold_start",
                "overall_accuracy": 0,
                "total_attempts": 0,
                "total_correct": 0,
                "topic_performance": {},
                "topics": [],
                "difficulties": ["easy"],
                "is_new_user": True
            }
        else:
            # Analyze existing progress
            from src.services.adaptive_quiz_service import AdaptiveQuizService
            quiz_service = AdaptiveQuizService()
            current_progress = quiz_service.analyze_user_progress(user_progress)
        
        # Use default user preferences (system decides)
        user_preferences = {
            "learning_style": "reading_writing",
            "time_available": 60,
            "focus_areas": []
        }
        
        # Get base learning path recommendation (rule-based)
        learning_path = learning_path_optimizer.get_next_learning_recommendation(
            user_id=user_id,
            current_progress=current_progress,
            user_preferences=user_preferences
        )
        
        # Get all available skills
        available_skills = learning_path_optimizer.get_all_available_skills()
        
        # Build base dashboard data
        dashboard_data = {
            "user_progress": {
                "user_id": user_id,
                "is_new_user": current_progress.get("is_new_user", False),
                "progress_summary": current_progress
            },
            "next_skill": learning_path.get("next_skill") if learning_path else None,
            "learning_path": learning_path.get("learning_path") if learning_path else None,
            "available_skills": available_skills,
            "milestones": learning_path.get("milestones") if learning_path else [],
            "alternative_paths": learning_path.get("alternative_paths") if learning_path else [],
            "total_estimated_time": learning_path.get("total_estimated_time") if learning_path else 0,
            "confidence_score": learning_path.get("confidence_score") if learning_path else 0,
            "enhancement_method": "rule_based"  # Default method
        }
        
        # 🚀 ENHANCE WITH LLM IF REQUESTED!
        if request.llm:
            try:
                print("🧠 Activating Gemini LLM enhancement...")
                
                # Create user context for LLM
                user_context = {
                    "user_id": user_id,
                    "learning_style": user_preferences.get("learning_style", "reading_writing"),
                    "current_level": "beginner" if current_progress.get("is_new_user") else "intermediate",
                    "time_available": user_preferences.get("time_available", 60),
                    "career_goals": "general_knowledge",  # Can be enhanced later
                    "progress_summary": current_progress
                }
                
                # Enhance next skill with personalized tips
                if dashboard_data["next_skill"]:
                    print("💡 Generating personalized learning tips with LLM...")
                    personalized_tips = await gemini_enhancer.generate_personalized_tips(
                        dashboard_data["next_skill"], 
                        user_context
                    )
                    dashboard_data["next_skill"]["learning_tips"] = personalized_tips
                    dashboard_data["next_skill"]["enhanced_by_llm"] = True
                
                # Generate intelligent milestones
                print("🎯 Generating intelligent milestones with LLM...")
                try:
                    enhanced_milestones = await gemini_enhancer.generate_learning_milestones(
                        dashboard_data, 
                        user_context
                    )
                    if enhanced_milestones and isinstance(enhanced_milestones, list) and len(enhanced_milestones) > 0:
                        # Validate milestones before adding
                        validated_milestones = gemini_enhancer._validate_milestones(enhanced_milestones)
                        if validated_milestones:
                            dashboard_data["milestones"] = validated_milestones
                            dashboard_data["milestones_enhanced_by_llm"] = True
                            print(f"✅ Successfully generated and validated {len(validated_milestones)} milestones")
                        else:
                            print("⚠️ Milestone validation failed, using fallback")
                            dashboard_data["milestones"] = gemini_enhancer._get_fallback_milestones(dashboard_data)
                    else:
                        print("⚠️ No milestones generated, using fallback")
                        dashboard_data["milestones"] = gemini_enhancer._get_fallback_milestones(dashboard_data)
                except Exception as e:
                    print(f"⚠️ Error generating milestones: {e}")
                    dashboard_data["milestones"] = gemini_enhancer._get_fallback_milestones(dashboard_data)
                
                # Analyze skill gaps intelligently
                print("🔍 Analyzing skill gaps with LLM...")
                priority_skills = await gemini_enhancer.analyze_skill_gaps_intelligently(
                    current_progress, 
                    available_skills
                )
                if priority_skills:
                    dashboard_data["llm_priority_skills"] = priority_skills
                
                # Generate comprehensive enhancements
                print("🚀 Generating comprehensive learning enhancements with LLM...")
                comprehensive_enhancements = await gemini_enhancer.generate_comprehensive_enhancements(
                    dashboard_data,
                    user_context,
                    current_progress
                )
                
                # Merge comprehensive enhancements with consistent structure
                if comprehensive_enhancements.get("enhanced_recommendations"):
                    # Initialize if not exists
                    if "enhanced_recommendations" not in dashboard_data:
                        dashboard_data["enhanced_recommendations"] = {}
                    
                    # Ensure all required fields exist
                    required_fields = [
                        "personalized_strategies", "study_schedule", "real_world_applications",
                        "progress_tracking", "adaptive_learning", "motivation_insights",
                        "complementary_resources", "difficulty_progression", "gamification_elements"
                    ]
                    
                    for field in required_fields:
                        if field not in dashboard_data["enhanced_recommendations"]:
                            dashboard_data["enhanced_recommendations"][field] = [] if field.endswith('s') else {}
                    
                    # Merge the enhancements
                    for key, value in comprehensive_enhancements["enhanced_recommendations"].items():
                        if key in dashboard_data["enhanced_recommendations"]:
                            if isinstance(value, list) and isinstance(dashboard_data["enhanced_recommendations"][key], list):
                                # Merge lists, avoiding duplicates
                                existing_items = {str(item) for item in dashboard_data["enhanced_recommendations"][key]}
                                for item in value:
                                    if str(item) not in existing_items:
                                        dashboard_data["enhanced_recommendations"][key].append(item)
                            elif isinstance(value, dict) and isinstance(dashboard_data["enhanced_recommendations"][key], dict):
                                # Merge dictionaries
                                dashboard_data["enhanced_recommendations"][key].update(value)
                            else:
                                # Replace non-list/dict values
                                dashboard_data["enhanced_recommendations"][key] = value
                        else:
                            # Add new field
                            dashboard_data["enhanced_recommendations"][key] = value
                    
                    dashboard_data["enhancements_enhanced_by_llm"] = True
                
                # Enhance overall learning path
                print("🧠 Enhancing overall learning path with LLM...")
                enhanced_path = await gemini_enhancer.enhance_learning_path(
                    dashboard_data, 
                    user_context
                )
                
                # Merge any additional enhanced data with consistent structure
                if enhanced_path.get("enhanced_recommendations"):
                    # Ensure consistent structure
                    if "enhanced_recommendations" not in dashboard_data:
                        dashboard_data["enhanced_recommendations"] = {}
                    
                    # Ensure all required fields exist
                    required_fields = [
                        "personalized_strategies", "study_schedule", "real_world_applications",
                        "progress_tracking", "adaptive_learning", "motivation_insights",
                        "complementary_resources", "difficulty_progression", "gamification_elements"
                    ]
                    
                    for field in required_fields:
                        if field not in dashboard_data["enhanced_recommendations"]:
                            dashboard_data["enhanced_recommendations"][field] = [] if field.endswith('s') else {}
                    
                    # Merge with existing enhancements
                    for key, value in enhanced_path["enhanced_recommendations"].items():
                        if key in dashboard_data["enhanced_recommendations"]:
                            if isinstance(value, list) and isinstance(dashboard_data["enhanced_recommendations"][key], list):
                                # Merge lists, avoiding duplicates
                                existing_items = {str(item) for item in dashboard_data["enhanced_recommendations"][key]}
                                for item in value:
                                    if str(item) not in existing_items:
                                        dashboard_data["enhanced_recommendations"][key].append(item)
                            elif isinstance(value, dict) and isinstance(dashboard_data["enhanced_recommendations"][key], dict):
                                # Merge dictionaries
                                dashboard_data["enhanced_recommendations"][key].update(value)
                            else:
                                # Replace non-list/dict values
                                dashboard_data["enhanced_recommendations"][key] = value
                        else:
                            # Add new field
                            dashboard_data["enhanced_recommendations"][key] = value
                
                dashboard_data["enhancement_method"] = "llm_enhanced"
                dashboard_data["llm_enhancement_status"] = "success"
                
                # Validate final structure
                if "enhanced_recommendations" in dashboard_data:
                    dashboard_data["enhanced_recommendations"] = gemini_enhancer._validate_and_clean_enhancements(
                        dashboard_data["enhanced_recommendations"]
                    )
                
                if "milestones" in dashboard_data and dashboard_data["milestones"] is not None:
                    dashboard_data["milestones"] = gemini_enhancer._validate_milestones(
                        dashboard_data["milestones"]
                    )
                elif "milestones" not in dashboard_data or dashboard_data["milestones"] is None:
                    # Ensure milestones exist with fallback
                    dashboard_data["milestones"] = gemini_enhancer._get_fallback_milestones(dashboard_data)
                
                print("✅ LLM enhancement completed successfully!")
                
            except Exception as e:
                print(f"⚠️ LLM enhancement failed: {e}")
                dashboard_data["enhancement_method"] = "rule_based_fallback"
                dashboard_data["llm_enhancement_status"] = "failed"
                dashboard_data["llm_error"] = str(e)
                # Continue with rule-based data
        
        # Final validation to ensure consistent structure
        if "enhanced_recommendations" in dashboard_data:
            dashboard_data["enhanced_recommendations"] = gemini_enhancer._validate_and_clean_enhancements(
                dashboard_data["enhanced_recommendations"]
            )
        
        if "milestones" in dashboard_data and dashboard_data["milestones"] is not None:
            dashboard_data["milestones"] = gemini_enhancer._validate_milestones(
                dashboard_data["milestones"]
            )
        elif "milestones" not in dashboard_data or dashboard_data["milestones"] is None:
            # Ensure milestones exist with fallback
            dashboard_data["milestones"] = gemini_enhancer._get_fallback_milestones(dashboard_data)
        
        return LearningPathResponse(
            success=True,
            message=f"Learning dashboard generated successfully using {dashboard_data['enhancement_method']}",
            data=dashboard_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in learning dashboard: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate learning dashboard: {str(e)}"
        ) 
