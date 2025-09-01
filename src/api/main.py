from dotenv import load_dotenv
load_dotenv()
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from src.rag.graph import build_rag_graph

from src.services.adaptive_quiz_service import adaptive_quiz_service
from src.models.quiz_models import AdaptiveQuizRequest, AdaptiveQuizResponse
from src.services.learning_path_optimizer import learning_path_optimizer
from src.models.learning_path_models import LearningPathRequest, LearningPathResponse
from src.services.gemini_learning_enhancer import gemini_enhancer
from src.services.metrics_service import metrics_service
from src.services.ragas_evaluation_service import ragas_evaluation_service
from src.services.phoenix_integration_service import phoenix_integration_service

from src.agents.internet_search_agent import run_internet_search


app = FastAPI(
    title="Tutor Backend API",
    description="AI-powered tutoring and learning management system with adaptive quizzes, learning paths, and intelligent content retrieval",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Core Learning API",
            "description": "Core endpoints for learning, quizzes, and content retrieval"
        },
        {
            "name": "System Metrics",
            "description": "System performance monitoring and analytics endpoints"
        },
        {
            "name": "System",
            "description": "Basic system endpoints for health checks and root access"
        }
    ]
)

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

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Tutor Backend API",
        "status": "running",
        "version": "1.0.0"
    }

class QueryRequest(BaseModel):
    query: str
    use_llm: bool = False
    enable_reranking: bool = False
    reranking_strategy: str = "semantic_relevance"
    enable_evaluation: bool = False  # NEW: Enable RAGAS evaluation
    ground_truth: Optional[str] = None  # NEW: Optional ground truth for evaluation

class QueryResponse(BaseModel):
    response: dict
    evaluation: Optional[dict] = None  # NEW: RAGAS evaluation results



@app.post("/query", response_model=QueryResponse, tags=["Core Learning API"])
def query_endpoint(request: QueryRequest):
    start_time = time.time()
    try:
        inputs = request.dict()
        inputs["model_type"] = "gemini"
        inputs["model_name"] = "gemini-1.5-flash"
        
        # Add reranking parameters to inputs
        inputs["enable_reranking"] = request.enable_reranking
        inputs["reranking_strategy"] = request.reranking_strategy
        
        result = rag_graph.invoke(inputs)
        
        # Extract response and context for evaluation
        response_data = result.get("response", {})
        context = result.get("context", [])
        
        # Generate response text for evaluation
        response_text = ""
        if request.use_llm and "explanation" in response_data:
            response_text = response_data["explanation"]
        elif "questions" in response_data and response_data["questions"]:
            # Use first question as response text for evaluation
            first_question = response_data["questions"][0]
            if isinstance(first_question, dict):
                response_text = first_question.get("question", str(first_question))
            else:
                response_text = str(first_question)
        else:
            response_text = str(response_data)
        
        # Perform RAGAS evaluation if requested
        evaluation_dict = None
        if request.enable_evaluation:
            try:
                evaluation_result = ragas_evaluation_service.evaluate_rag_quality(
                    query=request.query,
                    context=context,
                    response=response_text,
                    ground_truth=request.ground_truth
                )
                
                # Convert evaluation result to dict for API response
                evaluation_dict = {
                    "metrics": {
                        "context_precision": evaluation_result.metrics.context_precision,
                        "faithfulness": evaluation_result.metrics.faithfulness,
                        "answer_correctness": evaluation_result.metrics.answer_correctness,
                        "context_relevancy": evaluation_result.metrics.context_relevancy,
                        "overall_score": evaluation_result.metrics.overall_score,
                        "evaluation_time": evaluation_result.metrics.evaluation_time
                    },
                    "quality_insights": evaluation_result.quality_insights,
                    "recommendations": evaluation_result.recommendations,
                    "metadata": evaluation_result.metrics.metadata
                }
                
                # Record evaluation metrics
                metrics_service.record_api_call(
                    endpoint="/query",
                    use_llm=request.use_llm,
                    response_time=time.time() - start_time,
                    success=True,
                    additional_metrics={
                        "ragas_context_precision": evaluation_result.metrics.context_precision,
                        "ragas_faithfulness": evaluation_result.metrics.faithfulness,
                        "ragas_answer_correctness": evaluation_result.metrics.answer_correctness,
                        "ragas_context_relevancy": evaluation_result.metrics.context_relevancy,
                        "ragas_overall_score": evaluation_result.metrics.overall_score
                    }
                )
                
            except Exception as eval_error:
                print(f"⚠️ RAGAS evaluation failed: {eval_error}")
                evaluation_dict = {
                    "error": f"Evaluation failed: {str(eval_error)}",
                    "status": "evaluation_failed"
                }
        else:
            # Record successful API call without evaluation
            response_time = time.time() - start_time
            metrics_service.record_api_call(
                endpoint="/query",
                use_llm=request.use_llm,
                response_time=response_time,
                success=True
            )
        
        return {
            "response": response_data,
            "evaluation": evaluation_dict
        }
        
    except Exception as e:
        # Record failed API call
        response_time = time.time() - start_time
        metrics_service.record_api_call(
            endpoint="/query",
            use_llm=request.use_llm,
            response_time=response_time,
            success=False
        )
        raise HTTPException(status_code=500, detail=str(e))





@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/phoenix/start", tags=["System"])
def start_phoenix_server():
    """Start Phoenix server for LLM observability"""
    try:
        success = phoenix_integration_service.start_phoenix_server()
        if success:
            return {
                "status": "success",
                "message": "Phoenix server started successfully",
                "phoenix_url": phoenix_integration_service.get_phoenix_url(),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start Phoenix server")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting Phoenix server: {str(e)}")

@app.get("/phoenix/status", tags=["System"])
def get_phoenix_status():
    """Get Phoenix server status"""
    return {
        "phoenix_available": phoenix_integration_service.phoenix_available,
        "phoenix_url": phoenix_integration_service.get_phoenix_url(),
        "port": phoenix_integration_service.port,
        "timestamp": datetime.utcnow().isoformat()
    }

# === Quiz Detail Endpoint (Internet Search) ===

class QuizDetailRequest(BaseModel):
    query: str
    use_llm: bool = False
    enable_reranking: bool = False
    reranking_strategy: str = "semantic_relevance"
    enable_evaluation: bool = False  # NEW: Enable RAGAS evaluation
    ground_truth: Optional[str] = None  # NEW: Optional ground truth for evaluation

@app.post("/quiz-detail", tags=["Core Learning API"])
def get_quiz_detail(request: QuizDetailRequest):
    """
    Get internet search results for quiz questions using LangGraph and SerperDev
    """
    start_time = time.time()
    
    # Start Phoenix tracing
    trace_id = phoenix_integration_service.log_quiz_detail_request(
        query=request.query,
        use_llm=request.use_llm,
        enable_reranking=request.enable_reranking,
        reranking_strategy=request.reranking_strategy,
        enable_evaluation=request.enable_evaluation,
        ground_truth=request.ground_truth
    )
    
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Log search start
        search_start_time = time.time()
        
        result = run_internet_search(
            query=request.query.strip(),
            use_llm=request.use_llm,
            enable_reranking=request.enable_reranking,
            reranking_strategy=request.reranking_strategy
        )
        
        # Log search results and performance
        search_time = time.time() - search_start_time
        search_results = result.get("results", [])
        phoenix_integration_service.log_search_results(
            trace_id=trace_id,
            search_results=search_results,
            search_time=search_time,
            reranking_applied=request.enable_reranking
        )
        
        if "error" in result:
            # Record failed API call
            response_time = time.time() - start_time
            metrics_service.record_api_call(
                endpoint="/quiz-detail",
                use_llm=request.use_llm,
                response_time=response_time,
                success=False
            )
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Extract response and context for evaluation
        response_data = result
        context = result.get("results", [])
        
        # Generate response text for evaluation
        response_text = ""
        if request.use_llm and "llm_summary" in result:
            response_text = result["llm_summary"]
            # Log LLM enhancement to Phoenix
            llm_time = time.time() - search_start_time
            phoenix_integration_service.log_llm_enhancement(
                trace_id=trace_id,
                query=request.query,
                search_results=search_results,
                llm_summary=response_text,
                llm_time=llm_time,
                model_used=result.get("model_used", "unknown")
            )
        elif "results" in result and result["results"]:
            # Use first result as response text for evaluation
            first_result = result["results"][0]
            if isinstance(first_result, dict):
                response_text = first_result.get("snippet", str(first_result))
            else:
                response_text = str(first_result)
        else:
            response_text = str(result)
        
        # Perform RAGAS evaluation if requested
        evaluation_dict = None
        if request.enable_evaluation:
            try:
                evaluation_result = ragas_evaluation_service.evaluate_rag_quality(
                    query=request.query,
                    context=context,
                    response=response_text,
                    ground_truth=request.ground_truth
                )
                
                # Convert evaluation result to dict for API response
                evaluation_dict = {
                    "metrics": {
                        "context_precision": evaluation_result.metrics.context_precision,
                        "faithfulness": evaluation_result.metrics.faithfulness,
                        "answer_correctness": evaluation_result.metrics.answer_correctness,
                        "context_relevancy": evaluation_result.metrics.context_relevancy,
                        "overall_score": evaluation_result.metrics.overall_score,
                        "evaluation_time": evaluation_result.metrics.evaluation_time
                    },
                    "quality_insights": evaluation_result.quality_insights,
                    "recommendations": evaluation_result.recommendations,
                    "metadata": evaluation_result.metrics.metadata
                }
                
                # Record evaluation metrics
                metrics_service.record_api_call(
                    endpoint="/quiz-detail",
                    use_llm=request.use_llm,
                    response_time=time.time() - start_time,
                    success=True,
                    additional_metrics={
                        "ragas_context_precision": evaluation_result.metrics.context_precision,
                        "ragas_faithfulness": evaluation_result.metrics.faithfulness,
                        "ragas_answer_correctness": evaluation_result.metrics.answer_correctness,
                        "ragas_context_relevancy": evaluation_result.metrics.context_relevancy,
                        "ragas_overall_score": evaluation_result.metrics.overall_score
                    }
                )
                
            except Exception as eval_error:
                print(f"⚠️ RAGAS evaluation failed in quiz-detail: {eval_error}")
                evaluation_dict = {
                    "error": f"Evaluation failed: {str(eval_error)}",
                    "status": "evaluation_failed"
                }
        else:
            # Record successful API call without evaluation
            response_time = time.time() - start_time
            metrics_service.record_api_call(
                endpoint="/quiz-detail",
                use_llm=request.use_llm,
                response_time=response_time,
                success=True
            )
        
        # Log request completion to Phoenix
        total_time = time.time() - start_time
        phoenix_integration_service.log_request_completion(
            trace_id=trace_id,
            total_time=total_time,
            success=True
        )
        
        # Return result with optional evaluation
        if request.enable_evaluation:
            return {
                **result,
                "evaluation": evaluation_dict
            }
        else:
            return result
        
    except HTTPException:
        # Log error completion to Phoenix
        total_time = time.time() - start_time
        phoenix_integration_service.log_request_completion(
            trace_id=trace_id,
            total_time=total_time,
            success=False,
            error_message="HTTP Exception"
        )
        raise
    except Exception as e:
        # Log error completion to Phoenix
        total_time = time.time() - start_time
        phoenix_integration_service.log_request_completion(
            trace_id=trace_id,
            total_time=total_time,
            success=False,
            error_message=str(e)
        )
        
        # Record failed API call
        response_time = time.time() - start_time
        metrics_service.record_api_call(
            endpoint="/quiz-detail",
            use_llm=request.use_llm,
            response_time=response_time,
            success=False
        )
        print(f"❌ Error in quiz-detail endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz details: {str(e)}")

# === System Metrics Dashboard ===

@app.get("/metrics/dashboard", tags=["System Metrics"])
def get_system_metrics():
    """
    Get comprehensive system performance metrics and statistics
    """
    try:
        metrics = metrics_service.get_system_metrics()
        return metrics
    except Exception as e:
        print(f"❌ Error in metrics dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")

@app.get("/metrics/summary", tags=["System Metrics"])
def get_metrics_summary():
    """
    Get a summary of system performance with insights and recommendations
    """
    try:
        summary = metrics_service.get_metrics_summary()
        return summary
    except Exception as e:
        print(f"❌ Error in metrics summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics summary: {str(e)}")

@app.get("/metrics/trends", tags=["System Metrics"])
def get_performance_trends(days: int = 30):
    """
    Get performance trends over time
    """
    try:
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
        
        trends = metrics_service.get_performance_trends(days)
        return {"trends": trends, "period_days": days}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in performance trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

@app.get("/metrics/realtime", tags=["System Metrics"])
def get_real_time_metrics():
    """
    Get real-time system monitoring metrics
    """
    try:
        realtime = metrics_service.get_real_time_metrics()
        return realtime
    except Exception as e:
        print(f"❌ Error in real-time metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch real-time metrics: {str(e)}")



# === Adaptive Quiz Questions Endpoint ===

@app.post("/quiz/adaptive-questions", response_model=AdaptiveQuizResponse, tags=["Core Learning API"])
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

@app.post("/learning-path/dashboard", response_model=LearningPathResponse, tags=["Core Learning API"])
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
