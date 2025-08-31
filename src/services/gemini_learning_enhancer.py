"""
Gemini LLM Learning Path Enhancer
Uses Google's Gemini LLM to provide intelligent, personalized learning recommendations
"""
import os
import google.generativeai as genai
from typing import Dict, List, Optional
import json
from src.models.learning_path_models import (
    EnhancedRecommendations, Milestone, PersonalizedStrategy, StudySchedule,
    RealWorldApplication, ProgressTracking, AdaptiveLearning, ComplementaryResource,
    DifficultyProgression, GamificationElement
)

class GeminiLearningEnhancer:
    def __init__(self):
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _get_standardized_enhancement_structure(self) -> Dict:
        """
        Return the standardized structure for enhanced_recommendations
        This ensures consistency across all LLM enhancements
        """
        return {
            "personalized_strategies": [],
            "study_schedule": {},
            "real_world_applications": [],
            "progress_tracking": {},
            "adaptive_learning": {},
            "motivation_insights": [],
            "complementary_resources": [],
            "difficulty_progression": {},
            "gamification_elements": []
        }
    
    def _validate_and_clean_enhancements(self, data: Dict) -> Dict:
        """
        Validate and clean enhanced_recommendations using Pydantic models
        """
        try:
            # Validate the entire structure
            validated = EnhancedRecommendations(**data)
            return validated.model_dump()
        except Exception as e:
            print(f"⚠️ Validation failed, cleaning data: {e}")
            # Clean and fix the data
            cleaned = self._get_standardized_enhancement_structure()
            
            # Try to extract valid data from each field
            for field, default_value in cleaned.items():
                if field in data and data[field] is not None:
                    try:
                        if field == "personalized_strategies" and isinstance(data[field], list):
                            strategies = []
                            for item in data[field]:
                                if isinstance(item, dict):
                                    # Provide defaults for missing fields
                                    strategy_data = {
                                        "strategy_name": item.get("strategy_name", "Learning Strategy"),
                                        "description": item.get("description", "Strategy description"),
                                        "when_to_use": item.get("when_to_use", "When to use this strategy"),
                                        "expected_outcome": item.get("expected_outcome", "Expected results")
                                    }
                                    strategies.append(strategy_data)
                            cleaned[field] = strategies
                        elif field == "study_schedule" and isinstance(data[field], dict):
                            schedule_data = {
                                "daily_routine": data[field].get("daily_routine", "30 minutes of focused study"),
                                "weekly_structure": data[field].get("weekly_structure", "5 days of study, 2 days of review"),
                                "session_lengths": data[field].get("session_lengths", "30-45 minute sessions"),
                                "break_schedule": data[field].get("break_schedule", "5-minute breaks every 25 minutes"),
                                "review_frequency": data[field].get("review_frequency", "Weekly review")
                            }
                            cleaned[field] = schedule_data
                        elif field == "real_world_applications" and isinstance(data[field], list):
                            applications = []
                            for item in data[field]:
                                if isinstance(item, dict):
                                    app_data = {
                                        "skill": item.get("skill", "General Skill"),
                                        "application": item.get("application", "Real-world application"),
                                        "project_idea": item.get("project_idea", "Project suggestion"),
                                        "career_relevance": item.get("career_relevance", "Career benefits")
                                    }
                                    applications.append(app_data)
                            cleaned[field] = applications
                        elif field == "progress_tracking" and isinstance(data[field], dict):
                            tracking_data = {
                                "milestone_system": data[field].get("milestone_system", "Track completion of each skill"),
                                "performance_metrics": data[field].get("performance_metrics", "Accuracy and completion time"),
                                "goal_setting": data[field].get("goal_setting", "Set weekly learning targets"),
                                "motivation_system": data[field].get("motivation_system", "Celebrate completed milestones")
                            }
                            cleaned[field] = tracking_data
                        elif field == "adaptive_learning" and isinstance(data[field], dict):
                            adaptive_data = {
                                "difficulty_adjustment": data[field].get("difficulty_adjustment", "Increase difficulty after 80% accuracy"),
                                "skill_progression": data[field].get("skill_progression", "Move to next skill after mastering current"),
                                "remedial_strategies": data[field].get("remedial_strategies", "Review basics if struggling"),
                                "success_indicators": data[field].get("success_indicators", "Consistent 80%+ accuracy")
                            }
                            cleaned[field] = adaptive_data
                        elif field == "motivation_insights" and isinstance(data[field], list):
                            cleaned[field] = [str(item) for item in data[field] if item]
                        elif field == "complementary_resources" and isinstance(data[field], list):
                            resources = []
                            for item in data[field]:
                                if isinstance(item, dict):
                                    resource_data = {
                                        "resource_type": item.get("resource_type", "Website"),
                                        "name": item.get("name", "Learning Resource"),
                                        "description": item.get("description", "Resource description"),
                                        "link": item.get("link")
                                    }
                                    resources.append(resource_data)
                            cleaned[field] = resources
                        elif field == "difficulty_progression" and isinstance(data[field], dict):
                            progression_data = {
                                "approach": data[field].get("approach", "Master each level before progressing"),
                                "polity_strategy": data[field].get("polity_strategy", "Focus on fundamentals first"),
                                "environment_strategy": data[field].get("environment_strategy", "Build conceptual understanding"),
                                "current_affairs_strategy": data[field].get("current_affairs_strategy", "Stay updated with daily practice"),
                                "economy_strategy": data[field].get("economy_strategy", "Apply concepts to real scenarios")
                            }
                            cleaned[field] = progression_data
                        elif field == "gamification_elements" and isinstance(data[field], list):
                            elements = []
                            for item in data[field]:
                                if isinstance(item, dict):
                                    element_data = {
                                        "element": item.get("element", "Gamification Element"),
                                        "description": item.get("description", "Element description")
                                    }
                                    elements.append(element_data)
                            cleaned[field] = elements
                    except Exception as field_error:
                        print(f"⚠️ Error processing field {field}: {field_error}")
                        cleaned[field] = default_value
                else:
                    cleaned[field] = default_value
            
            return cleaned

    def _validate_milestones(self, milestones: List[Dict]) -> List[Dict]:
        """
        Validate and clean milestones using Pydantic models
        """
        try:
            # Handle None or invalid input
            if not milestones or not isinstance(milestones, list):
                print(f"⚠️ Invalid milestones input: {type(milestones)}")
                return self._get_fallback_milestones({})
            
            validated_milestones = []
            for i, milestone_data in enumerate(milestones):
                try:
                    # Ensure milestone_data is a dictionary
                    if not isinstance(milestone_data, dict):
                        print(f"⚠️ Milestone {i} is not a dict: {type(milestone_data)}")
                        continue
                    
                    # Provide default values for missing required fields
                    default_milestone = {
                        "milestone_id": f"milestone_{i+1}",
                        "name": "Learning Milestone",
                        "description": "Complete this learning objective",
                        "success_criteria": ["Understand the concept", "Complete practice exercises"],
                        "estimated_time": 30,
                        "difficulty": "beginner",
                        "motivation": "Build your knowledge foundation",
                        "practical_application": "Apply concepts to real scenarios",
                        "reward": "Progress to next level",
                        "prerequisites": []
                    }
                    
                    # Merge with provided data, using defaults for missing fields
                    for key, default_value in default_milestone.items():
                        if key not in milestone_data or milestone_data[key] is None:
                            milestone_data[key] = default_value
                    
                    # Validate with Pydantic
                    milestone = Milestone(**milestone_data)
                    validated_milestones.append(milestone.model_dump())
                    
                except Exception as e:
                    print(f"⚠️ Invalid milestone data for milestone {i}: {e}")
                    print(f"⚠️ Milestone data: {milestone_data}")
                    
                    # Create a fallback milestone
                    fallback = Milestone(
                        milestone_id=f"milestone_{len(validated_milestones)+1}",
                        name="Learning Milestone",
                        description="Complete this learning objective",
                        success_criteria=["Understand the concept", "Complete practice exercises"],
                        estimated_time=30,
                        difficulty="beginner",
                        motivation="Build strong foundation for advanced topics",
                        practical_application="Apply concepts to simple scenarios",
                        reward="Progress to next level",
                        prerequisites=[]
                    )
                    validated_milestones.append(fallback.model_dump())
            
            return validated_milestones
        except Exception as e:
            print(f"⚠️ Milestone validation failed: {e}")
            return self._get_fallback_milestones({})

    def _merge_enhancements(self, existing: Dict, new: Dict) -> Dict:
        """
        Merge new enhancements with existing ones, maintaining structure
        """
        if not existing:
            existing = self._get_standardized_enhancement_structure()
        
        # Ensure all required fields exist
        for field in self._get_standardized_enhancement_structure().keys():
            if field not in existing:
                existing[field] = self._get_standardized_enhancement_structure()[field]
        
        # Merge new data
        for field, value in new.items():
            if field in existing:
                if isinstance(value, list) and isinstance(existing[field], list):
                    # Merge lists, avoiding duplicates
                    existing_ids = {item.get('id', item.get('name', str(item))) for item in existing[field] if item}
                    for item in value:
                        item_id = item.get('id', item.get('name', str(item)))
                        if item_id not in existing_ids:
                            existing[field].append(item)
                elif isinstance(value, dict) and isinstance(existing[field], dict):
                    # Merge dictionaries
                    existing[field].update(value)
                else:
                    # Replace non-list/dict values
                    existing[field] = value
            else:
                # Add new field
                existing[field] = value
        
        return existing

    async def enhance_learning_path(self, base_path: Dict, user_context: Dict) -> Dict:
        """
        Enhance learning path with LLM-powered insights
        Note: This method focuses on general enhancements, not milestones (which are handled separately)
        """
        try:
            # Create comprehensive prompt for LLM
            prompt = self._create_enhancement_prompt(base_path, user_context)
            
            # Get LLM response
            response = await self._get_llm_response(prompt)
            
            # Parse and integrate LLM insights (excluding milestones)
            enhanced_path = self._integrate_llm_insights_excluding_milestones(base_path, response)
            
            return enhanced_path
            
        except Exception as e:
            print(f"⚠️ LLM enhancement failed: {e}")
            # Return base path if LLM fails
            return base_path

    def _integrate_llm_insights_excluding_milestones(self, base_path: Dict, response: str) -> Dict:
        """
        Integrate LLM insights with base learning path data, excluding milestones
        """
        enhanced_path = base_path.copy()
        
        try:
            print(f"🔍 Parsing LLM response...")
            print(f"🔍 Response type: {type(response)}")
            print(f"🔍 Response preview: {str(response)[:300]}...")
            
            # Parse LLM response
            llm_insights = self._parse_llm_response(response)
            
            print(f"🔍 Parsed insights type: {type(llm_insights)}")
            print(f"🔍 Parsed insights keys: {list(llm_insights.keys()) if isinstance(llm_insights, dict) else 'Not a dict'}")
            
            # Ensure llm_insights is a dictionary
            if not isinstance(llm_insights, dict):
                print(f"⚠️ LLM insights is not a dictionary: {type(llm_insights)}")
                return enhanced_path
            
            # Skip milestones - they're handled separately by generate_learning_milestones
            print("ℹ️ Skipping milestones in enhance_learning_path (handled separately)")
            
            # Add enhanced recommendations if available - ensure consistent structure
            if llm_insights.get("enhanced_recommendations"):
                enhanced_recs = llm_insights["enhanced_recommendations"]
                if isinstance(enhanced_recs, dict) and len(enhanced_recs) > 0:
                    # Initialize if not exists
                    if "enhanced_recommendations" not in enhanced_path:
                        enhanced_path["enhanced_recommendations"] = self._get_standardized_enhancement_structure()
                    
                    # Merge with standardized structure
                    enhanced_path["enhanced_recommendations"] = self._merge_enhancements(
                        enhanced_path["enhanced_recommendations"],
                        enhanced_recs
                    )
                    print(f"✅ Successfully integrated enhanced recommendations with {len(enhanced_recs)} fields")
                else:
                    print(f"⚠️ Enhanced recommendations is not a valid dict: {type(enhanced_recs)} (length: {len(enhanced_recs) if isinstance(enhanced_recs, dict) else 'N/A'})")
            else:
                print("ℹ️ No enhanced recommendations found in LLM insights")
            
            # Add personalized strategies if available
            if llm_insights.get("personalized_strategies"):
                strategies = llm_insights["personalized_strategies"]
                if isinstance(strategies, list):
                    enhanced_path["personalized_strategies"] = strategies
                else:
                    print(f"⚠️ Personalized strategies is not a list: {type(strategies)}")
            
            # Add study schedule if available
            if llm_insights.get("study_schedule"):
                schedule = llm_insights["study_schedule"]
                if isinstance(schedule, dict):
                    enhanced_path["study_schedule"] = schedule
                else:
                    print(f"⚠️ Study schedule is not a dict: {type(schedule)}")
            
            # Add real-world applications if available
            if llm_insights.get("real_world_applications"):
                applications = llm_insights["real_world_applications"]
                if isinstance(applications, list):
                    enhanced_path["real_world_applications"] = applications
                else:
                    print(f"⚠️ Real world applications is not a list: {type(applications)}")
            
            print(f"✅ Integrated {len(llm_insights)} LLM insights (excluding milestones)")
            
        except Exception as e:
            print(f"⚠️ Error integrating LLM insights: {e}")
            print(f"⚠️ Response type: {type(response)}")
            print(f"⚠️ Response preview: {str(response)[:200]}...")
        
        return enhanced_path
    
    async def generate_personalized_tips(self, skill: Dict, user_context: Dict) -> List[str]:
        """
        Generate personalized learning tips using LLM
        """
        try:
            prompt = f"""
            As an expert learning coach, generate 5 personalized learning tips for this skill:
            
            Skill: {skill.get('name', 'Unknown')}
            Difficulty: {skill.get('difficulty', 'Unknown')}
            Estimated Time: {skill.get('estimated_time', 0)} minutes
            
            User Context:
            - Learning Style: {user_context.get('learning_style', 'Not specified')}
            - Current Level: {user_context.get('current_level', 'Beginner')}
            - Time Available: {user_context.get('time_available', 60)} minutes per day
            - Career Goals: {user_context.get('career_goals', 'General knowledge')}
            
            Generate tips that are:
            1. Specific to this skill and difficulty level
            2. Tailored to the user's learning style
            3. Practical and actionable
            4. Consider time constraints
            5. Relevant to career goals
            
            Return only the tips as a JSON array of strings.
            """
            
            response = await self._get_llm_response(prompt)
            tips = self._parse_tips_response(response)
            
            return tips if tips else self._get_fallback_tips(skill)
            
        except Exception as e:
            print(f"⚠️ LLM tips generation failed: {e}")
            return self._get_fallback_tips(skill)
    
    async def analyze_skill_gaps_intelligently(self, user_progress: Dict, available_skills: List) -> List[str]:
        """
        Use LLM to intelligently analyze skill gaps and suggest improvements
        """
        try:
            prompt = f"""
            As an expert learning analyst, analyze this user's progress and suggest skill improvements:
            
            User Progress:
            {json.dumps(user_progress, indent=2)}
            
            Available Skills:
            {json.dumps(available_skills, indent=2)}
            
            Analyze and provide:
            1. Top 3-5 skills the user should focus on next
            2. Why these skills are important for their current level
            3. How these skills build upon their existing knowledge
            4. Estimated time investment for each skill
            5. Specific learning strategies for each skill
            6. How to overcome current learning barriers
            
            Consider:
            - User's current accuracy levels in different topics
            - Missing difficulty levels (easy/medium/hard)
            - Prerequisites and skill dependencies
            - Learning style preferences
            - Time constraints and realistic goals
            
            Return as JSON with structure:
            {{
                "priority_skills": [
                    {{
                        "skill_id": "skill_name",
                        "priority_reason": "why important",
                        "builds_on": "existing knowledge",
                        "time_investment": "estimated time",
                        "learning_strategy": "how to approach this skill",
                        "current_barrier": "what's holding them back",
                        "overcome_strategy": "how to overcome barriers"
                    }}
                ],
                "overall_analysis": {{
                    "strengths": ["what user is good at"],
                    "weaknesses": ["areas needing improvement"],
                    "opportunities": ["skills to capitalize on"],
                    "threats": ["potential learning obstacles"]
                }}
            }}
            """
            
            response = await self._get_llm_response(prompt)
            analysis = self._parse_analysis_response(response)
            
            return analysis if analysis else self._get_fallback_analysis(user_progress, available_skills)
            
        except Exception as e:
            print(f"⚠️ LLM skill gap analysis failed: {e}")
            return self._get_fallback_analysis(user_progress, available_skills)
    
    async def generate_learning_milestones(self, learning_path: Dict, user_context: Dict) -> List[Dict]:
        """
        Generate intelligent learning milestones using LLM
        """
        try:
            # Create comprehensive milestone prompt with structured output requirement
            prompt = f"""
            As an expert learning path designer, create 5-7 meaningful milestones for this learning journey.
            
            Learning Path:
            {json.dumps(learning_path, indent=2)}
            
            User Context:
            {json.dumps(user_context, indent=2)}
            
            Create milestones that:
            1. Break down the learning into achievable chunks
            2. Provide clear success criteria and measurable goals
            3. Motivate continued progress with meaningful rewards
            4. Align with user's learning style and time constraints
            5. Include practical applications and real-world assessments
            6. Consider the user's current progress and skill gaps
            7. Create a clear path from beginner to advanced levels
            
            IMPORTANT: Return ONLY valid JSON with this EXACT structure. Do not include any other text:
            
            [
                {{
                    "milestone_id": "unique_id_string",
                    "name": "Milestone name",
                    "description": "What to achieve",
                    "success_criteria": ["criterion1", "criterion2", "criterion3"],
                    "estimated_time": 30,
                    "difficulty": "beginner",
                    "motivation": "why this milestone matters",
                    "practical_application": "how to apply knowledge",
                    "reward": "what user gains from completing this",
                    "prerequisites": ["what needs to be completed first"]
                }}
            ]
            
            Rules:
            - milestone_id: unique string identifier
            - name: descriptive milestone name
            - description: clear explanation of what to achieve
            - success_criteria: array of 3-5 specific, measurable criteria
            - estimated_time: integer in minutes (15-120)
            - difficulty: exactly "beginner", "intermediate", or "advanced"
            - motivation: inspiring reason why this matters
            - practical_application: how to use the knowledge
            - reward: what the user gains
            - prerequisites: array of milestone IDs or empty array
            
            Make milestones specific to the user's current level and learning goals.
            """
            
            response = await self._get_llm_response(prompt)
            milestones = self._parse_milestones_response(response)
            
            # Validate and clean the milestones
            if milestones:
                milestones = self._validate_milestones(milestones)
            
            return milestones if milestones else self._get_fallback_milestones(learning_path)
            
        except Exception as e:
            print(f"⚠️ LLM milestone generation failed: {e}")
            return self._get_fallback_milestones(learning_path)
    
    async def generate_comprehensive_enhancements(self, learning_path: Dict, user_context: Dict, user_progress: Dict) -> Dict:
        """
        Generate comprehensive learning enhancements including strategies, schedules, and applications
        """
        try:
            prompt = f"""
            As an expert AI learning coach, create comprehensive enhancements for this learning path.
            
            Learning Path:
            {json.dumps(learning_path, indent=2)}
            
            User Context:
            {json.dumps(user_context, indent=2)}
            
            User Progress:
            {json.dumps(user_progress, indent=2)}
            
            IMPORTANT: Return ONLY valid JSON with this EXACT structure. Do not include any other text:
            
            {{
                "enhanced_recommendations": {{
                    "personalized_strategies": [
                        {{
                            "strategy_name": "Strategy name",
                            "description": "What this strategy involves",
                            "when_to_use": "When to apply this strategy",
                            "expected_outcome": "What this will achieve"
                        }}
                    ],
                    "study_schedule": {{
                        "daily_routine": "Daily study plan",
                        "weekly_structure": "Weekly learning schedule",
                        "session_lengths": "Optimal session durations",
                        "break_schedule": "When to take breaks",
                        "review_frequency": "How often to review"
                    }},
                    "real_world_applications": [
                        {{
                            "skill": "Skill name",
                            "application": "Real-world use case",
                            "project_idea": "Project to apply knowledge",
                            "career_relevance": "How this helps career"
                        }}
                    ],
                    "progress_tracking": {{
                        "milestone_system": "How to track progress",
                        "performance_metrics": "What to measure",
                        "goal_setting": "How to set realistic goals",
                        "motivation_system": "Rewards and incentives"
                    }},
                    "adaptive_learning": {{
                        "difficulty_adjustment": "When to change difficulty",
                        "skill_progression": "When to move to next level",
                        "remedial_strategies": "How to handle struggles",
                        "success_indicators": "Signs of readiness for next step"
                    }},
                    "motivation_insights": [
                        "Motivational insight 1",
                        "Motivational insight 2",
                        "Motivational insight 3"
                    ],
                    "complementary_resources": [
                        {{
                            "resource_type": "Website/Book/Video/etc",
                            "name": "Resource name",
                            "description": "What this resource provides",
                            "link": "URL or reference"
                        }}
                    ],
                    "difficulty_progression": {{
                        "approach": "Overall approach to difficulty progression",
                        "polity_strategy": "Specific strategy for Polity",
                        "environment_strategy": "Specific strategy for Environment",
                        "current_affairs_strategy": "Specific strategy for Current Affairs",
                        "economy_strategy": "Specific strategy for Economy"
                    }},
                    "gamification_elements": [
                        {{
                            "element": "Element name",
                            "description": "What this element provides"
                        }}
                    ]
                }}
            }}
            
            Rules:
            - Follow this exact structure - do not add or remove fields
            - All text fields should be descriptive and actionable
            - Lists should contain 3-5 items
            - Make recommendations specific to the user's progress and goals
            - Ensure all strategies are practical and implementable
            """
            
            response = await self._get_llm_response(prompt)
            enhancements = self._parse_llm_response(response)
            
            # Validate and clean the enhancements
            if enhancements and "enhanced_recommendations" in enhancements:
                enhancements["enhanced_recommendations"] = self._validate_and_clean_enhancements(
                    enhancements["enhanced_recommendations"]
                )
            
            return enhancements if enhancements else self._get_fallback_enhancements()
            
        except Exception as e:
            print(f"⚠️ LLM comprehensive enhancement failed: {e}")
            return self._get_fallback_enhancements()

    def _get_fallback_enhancements(self) -> Dict:
        """
        Fallback enhancements if LLM fails - using standardized structure
        """
        return {
            "enhanced_recommendations": {
                "personalized_strategies": [
                    {
                        "strategy_name": "Progressive Learning",
                        "description": "Start with basics and gradually increase difficulty",
                        "when_to_use": "For all new skills",
                        "expected_outcome": "Solid foundation and confidence"
                    }
                ],
                "study_schedule": {
                    "daily_routine": "30 minutes of focused study",
                    "weekly_structure": "5 days of study, 2 days of review",
                    "session_lengths": "30-45 minute sessions",
                    "break_schedule": "5-minute breaks every 25 minutes",
                    "review_frequency": "Weekly review of completed topics"
                },
                "real_world_applications": [
                    {
                        "skill": "Current Affairs",
                        "application": "Daily news discussions",
                        "project_idea": "Create a news summary",
                        "career_relevance": "Improves general knowledge and communication"
                    }
                ],
                "progress_tracking": {
                    "milestone_system": "Track completion of each skill",
                    "performance_metrics": "Accuracy and completion time",
                    "goal_setting": "Set weekly learning targets",
                    "motivation_system": "Celebrate completed milestones"
                },
                "adaptive_learning": {
                    "difficulty_adjustment": "Increase difficulty after 80% accuracy",
                    "skill_progression": "Move to next skill after mastering current",
                    "remedial_strategies": "Review basics if struggling",
                    "success_indicators": "Consistent 80%+ accuracy"
                },
                "motivation_insights": [
                    "Focus on progress, not perfection",
                    "Celebrate small wins daily",
                    "Remember your long-term goals"
                ],
                "complementary_resources": [
                    {
                        "resource_type": "Website",
                        "name": "Khan Academy",
                        "description": "Free educational resources on various topics",
                        "link": "https://www.khanacademy.org"
                    }
                ],
                "difficulty_progression": {
                    "approach": "Master each level before progressing",
                    "polity_strategy": "Focus on fundamentals first",
                    "environment_strategy": "Build conceptual understanding",
                    "current_affairs_strategy": "Stay updated with daily practice",
                    "economy_strategy": "Apply concepts to real scenarios"
                },
                "gamification_elements": [
                    {
                        "element": "Progress Tracking",
                        "description": "Visual progress indicators and milestones"
                    }
                ]
            }
        }
    
    def _create_enhancement_prompt(self, base_path: Dict, user_context: Dict) -> str:
        """
        Create comprehensive prompt for LLM enhancement
        """
        return f"""
        As an expert AI learning coach, enhance this learning path to make it more personalized and effective.
        
        Current Learning Path:
        {json.dumps(base_path, indent=2)}
        
        User Context:
        {json.dumps(user_context, indent=2)}
        
        IMPORTANT: Return ONLY valid JSON with this EXACT structure. Do not include any other text:
        
        {{
            "enhanced_recommendations": {{
                "personalized_strategies": [
                    {{
                        "strategy_name": "Strategy name",
                        "description": "What this strategy involves",
                        "when_to_use": "When to apply this strategy",
                        "expected_outcome": "What this will achieve"
                    }}
                ],
                "study_schedule": {{
                    "daily_routine": "Daily study plan",
                    "weekly_structure": "Weekly learning schedule",
                    "session_lengths": "Optimal session durations",
                    "break_schedule": "When to take breaks",
                    "review_frequency": "How often to review"
                }},
                "real_world_applications": [
                    {{
                        "skill": "Skill name",
                        "application": "Real-world use case",
                        "project_idea": "Project to apply knowledge",
                        "career_relevance": "How this helps career"
                    }}
                ],
                "progress_tracking": {{
                    "milestone_system": "How to track progress",
                    "performance_metrics": "What to measure",
                    "goal_setting": "How to set realistic goals",
                    "motivation_system": "Rewards and incentives"
                }},
                "adaptive_learning": {{
                    "difficulty_adjustment": "When to change difficulty",
                    "skill_progression": "When to move to next level",
                    "remedial_strategies": "How to handle struggles",
                    "success_indicators": "Signs of readiness for next step"
                }},
                "motivation_insights": [
                    "Motivational insight 1",
                    "Motivational insight 2",
                    "Motivational insight 3"
                ],
                "complementary_resources": [
                    {{
                        "resource_type": "Website/Book/Video/etc",
                        "name": "Resource name",
                        "description": "What this resource provides",
                        "link": "URL or reference"
                    }}
                ],
                "difficulty_progression": {{
                    "approach": "Overall approach to difficulty progression",
                    "polity_strategy": "Specific strategy for Polity",
                    "environment_strategy": "Specific strategy for Environment",
                    "current_affairs_strategy": "Specific strategy for Current Affairs",
                    "economy_strategy": "Specific strategy for Economy"
                }},
                "gamification_elements": [
                    {{
                        "element": "Element name",
                        "description": "What this element provides"
                    }}
                ]
            }}
        }}
        
        Rules:
        - Follow this exact structure - do not add or remove fields
        - All text fields should be descriptive and actionable
        - Lists should contain 3-5 items
        - Make recommendations specific to the user's progress and goals
        - Ensure all strategies are practical and implementable
        - Only return the JSON, no other text
        """
    
    async def _get_llm_response(self, prompt: str) -> str:
        """
        Get response from Gemini LLM with improved system instructions
        """
        try:
            # Add system-level instructions to ensure JSON-only output
            system_instruction = """
            You are a JSON-only API. You must respond with ONLY valid JSON.
            Do not include any explanatory text, markdown formatting, or other content.
            Do not use code blocks or backticks.
            Start your response with { and end with }.
            Ensure the JSON is properly formatted and valid.
            """
            
            enhanced_prompt = f"{system_instruction}\n\n{prompt}"
            
            response = self.model.generate_content(enhanced_prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini API call failed: {e}")
            raise
    
    def _clean_and_validate_json(self, json_str: str) -> Dict:
        """
        Clean and validate JSON string, handling common LLM formatting issues
        """
        try:
            # First try direct parsing
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        try:
            # Remove common LLM artifacts
            cleaned = json_str.strip()
            
            # Remove markdown formatting
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                if len(lines) > 2:
                    cleaned = '\n'.join(lines[1:-1])
            
            # Remove leading/trailing non-JSON text
            if not cleaned.startswith('{') and not cleaned.startswith('['):
                start = cleaned.find('{')
                if start == -1:
                    start = cleaned.find('[')
                if start != -1:
                    cleaned = cleaned[start:]
            
            if not cleaned.endswith('}') and not cleaned.endswith(']'):
                end = cleaned.rfind('}')
                if end == -1:
                    end = cleaned.rfind(']')
                if end != -1:
                    cleaned = cleaned[:end+1]
            
            # Normalize whitespace and newlines
            cleaned = cleaned.replace('\n', ' ').replace('\r', ' ')
            cleaned = ' '.join(cleaned.split())
            
            # Try parsing again
            return json.loads(cleaned)
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON cleaning failed: {e}")
            print(f"⚠️ Attempted to clean: {json_str[:200]}...")
            return {}

    def _parse_llm_response(self, response: str) -> Dict:
        """
        Parse LLM response and extract structured data
        Improved to handle responses with extra text before/after JSON
        """
        try:
            # Clean the response - remove common LLM artifacts
            cleaned_response = response.strip()
            
            # Remove markdown code blocks if present
            if "```json" in cleaned_response:
                start = cleaned_response.find("```json") + 7
                end = cleaned_response.find("```", start)
                if end != -1:
                    cleaned_response = cleaned_response[start:end].strip()
            elif "```" in cleaned_response:
                # Handle generic code blocks
                start = cleaned_response.find("```") + 3
                end = cleaned_response.find("```", start)
                if end != -1:
                    cleaned_response = cleaned_response[start:end].strip()
            
            # Try to find the largest valid JSON object
            best_json = {}
            max_length = 0
            
            # Look for JSON objects at different positions
            for start_char in ['{', '[', '{\n', '[\n']:
                start_pos = cleaned_response.find(start_char)
                if start_pos != -1:
                    # Find matching closing bracket
                    if start_char in ['{', '{\n']:
                        open_char, close_char = '{', '}'
                    else:
                        open_char, close_char = '[', ']'
                    
                    # Count brackets to find proper closing
                    bracket_count = 0
                    end_pos = -1
                    
                    for i, char in enumerate(cleaned_response[start_pos:], start_pos):
                        if char == open_char:
                            bracket_count += 1
                        elif char == close_char:
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_pos = i + 1
                                break
                    
                    if end_pos != -1:
                        try:
                            json_str = cleaned_response[start_pos:end_pos]
                            parsed = json.loads(json_str)
                            
                            # Check if this is a valid structure we want
                            if isinstance(parsed, dict) and len(parsed) > 0:
                                if len(json_str) > max_length:
                                    max_length = len(json_str)
                                    best_json = parsed
                        except json.JSONDecodeError:
                            continue
            
            # If we found a valid JSON object, return it
            if best_json:
                print(f"✅ Successfully parsed JSON from LLM response (length: {max_length})")
                return best_json
            
            # Fallback: try to extract any JSON-like structure and clean it
            if '{' in cleaned_response and '}' in cleaned_response:
                start = cleaned_response.find('{')
                end = cleaned_response.rfind('}') + 1
                json_str = cleaned_response[start:end]
                
                # Use the cleaning function
                cleaned_json = self._clean_and_validate_json(json_str)
                if cleaned_json:
                    return cleaned_json
            
            # If all else fails, try to parse the entire response as JSON
            try:
                # Sometimes the LLM returns pure JSON
                parsed = json.loads(cleaned_response)
                if isinstance(parsed, dict):
                    print("✅ Successfully parsed entire response as JSON")
                    return parsed
            except json.JSONDecodeError:
                pass
            
            print(f"⚠️ No valid JSON found in LLM response")
            print(f"⚠️ Response preview: {cleaned_response[:200]}...")
            return {}
            
        except Exception as e:
            print(f"⚠️ Error parsing LLM response: {e}")
            print(f"⚠️ Raw response: {response[:200]}...")
            return {}
    
    def _parse_tips_response(self, response: str) -> List[str]:
        """
        Parse tips from LLM response
        """
        try:
            parsed = self._parse_llm_response(response)
            if 'tips' in parsed:
                return parsed['tips']
            elif isinstance(parsed, list):
                return parsed
            else:
                return []
        except Exception:
            return []
    
    def _parse_analysis_response(self, response: str) -> List[str]:
        """
        Parse skill gap analysis from LLM response
        """
        try:
            parsed = self._parse_llm_response(response)
            if 'priority_skills' in parsed:
                return [skill['skill_id'] for skill in parsed['priority_skills']]
            else:
                return []
        except Exception:
            return []
    
    def _parse_milestones_response(self, response: str) -> List[Dict]:
        """
        Parse milestones from LLM response
        """
        try:
            parsed = self._parse_llm_response(response)
            if isinstance(parsed, list):
                return parsed
            else:
                return []
        except Exception:
            return []
    
    def _get_fallback_tips(self, skill: Dict) -> List[str]:
        """
        Fallback tips if LLM fails
        """
        return [
            f"Start with basic concepts for {skill.get('name', 'this skill')}",
            "Use visual aids and real-world examples",
            "Practice regularly with small sessions",
            "Connect new concepts to what you already know",
            "Review and reinforce learning periodically"
        ]
    
    def _get_fallback_analysis(self, user_progress: Dict, available_skills: List) -> List[str]:
        """
        Fallback skill gap analysis if LLM fails
        """
        # Simple rule-based fallback
        if not available_skills:
            return []
        
        # Return first 3 available skills as fallback
        return [skill['id'] for skill in available_skills[:3]]
    
    def _get_fallback_milestones(self, learning_path: Dict) -> List[Dict]:
        """
        Fallback milestones if LLM fails
        """
        return [
            {
                "milestone_id": "milestone_1",
                "name": "Complete Basic Concepts",
                "description": "Master fundamental principles",
                "success_criteria": ["Understand core concepts", "Complete practice exercises"],
                "estimated_time": 30,
                "motivation": "Build strong foundation for advanced topics",
                "practical_application": "Apply concepts to simple scenarios"
            }
        ]

# Global instance
gemini_enhancer = GeminiLearningEnhancer() 