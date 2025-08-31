"""
Adaptive Quiz Service - Handles user progress analysis and question recommendation
"""
from typing import List, Dict, Optional
from fastapi import HTTPException
from src.db.supabase_utils import get_user_topic_progress
from src.services.learning_path_optimizer import learning_path_optimizer

class AdaptiveQuizService:
    def __init__(self):
        pass
    
    def get_adaptive_quiz_questions(
        self, 
        jwt_token: str, 
        num_questions: int = 10, 
        topic_requests: List = None  # Can be List[TopicRequest] or List[Dict]
    ) -> Dict:
        """
        Get adaptive quiz questions based on user's topic progress
        """
        try:
            # Step 1: Extract user_id from JWT token
            print("🔐 Extracting user information from JWT...")
            
            # Import here to avoid circular imports
            from src.api.jwt_utils import get_user_from_jwt
            
            user_info = get_user_from_jwt(jwt_token)
            print(f"🔍 JWT decoded info: {user_info}")
            
            user_id = user_info.get("user_id")
            print(f"🔑 Extracted user_id: {user_id}")
            
            if not user_id:
                print(f"❌ User info keys: {list(user_info.keys())}")
                print(f"❌ Full user info: {user_info}")
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid JWT token: user_id not found"
                )
            
            print(f"✅ Extracted user_id: {user_id}")
            
            # Step 2: Get user's topic progress from Supabase
            print(f"🔍 Fetching progress for user: {user_id}")
            user_progress = get_user_topic_progress(user_id)
            
            if not user_progress:
                print("🆕 New user detected - providing cold start experience")
                # Create cold start progress analysis
                progress_analysis = {
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
                print(f"✅ Found {len(user_progress)} progress entries")
                # Step 3: Analyze progress to determine quiz strategy
                progress_analysis = self.analyze_user_progress(user_progress)
                print(f"📊 Progress analysis: {progress_analysis}")
            
            # Step 4: Get intelligent learning path recommendation
            learning_recommendation = self._get_learning_recommendation(
                user_id, progress_analysis, user_info
            )
            
            # Step 5: Build vector DB query filter based on progress
            if progress_analysis.get("is_new_user"):
                print("🎯 New user - building cold start filter")
                vector_filter = self.build_adaptive_filter(progress_analysis, None)  # No topics needed for cold start
            else:
                print(f"🎯 Building filter for topic_requests: {topic_requests}")
                vector_filter = self.build_adaptive_filter(progress_analysis, topic_requests)
            
            print(f"🎯 Vector filter: {vector_filter}")
            
            # Step 6: Fetch questions from vector database
            print(f"🔍 Calling vector DB with filter: {vector_filter}")
            questions = self.fetch_questions_from_vector_db(vector_filter, num_questions, user_id)
            print(f"📚 Fetched {len(questions)} questions from vector DB")
            print(f"📋 Raw questions data: {questions[:2] if questions else 'No questions'}")
            
            # Step 7: Format response
            quiz_questions = self.format_questions_for_quiz(questions)
            
            return {
                "user_id": user_id,
                "progress_summary": progress_analysis,
                "recommended_questions": quiz_questions,
                "quiz_strategy": progress_analysis.get("strategy", "balanced"),
                "is_new_user": progress_analysis.get("is_new_user", False),
                "learning_path": learning_recommendation
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in adaptive quiz service: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate adaptive quiz: {str(e)}")
    
    def _get_learning_recommendation(
        self, 
        user_id: str, 
        progress_analysis: Dict, 
        user_info: Dict
    ) -> Dict:
        """
        Get intelligent learning path recommendation
        """
        try:
            # Extract user preferences from JWT info
            user_preferences = {
                "learning_style": "reading_writing",  # Default, can be enhanced
                "time_available": 60,  # Default 60 minutes
                "focus_areas": progress_analysis.get("topics", [])
            }
            
            # Get next learning recommendation
            recommendation = learning_path_optimizer.get_next_learning_recommendation(
                user_id=user_id,
                current_progress=progress_analysis,
                user_preferences=user_preferences
            )
            
            print(f"🎯 Learning recommendation: {recommendation}")
            return recommendation
            
        except Exception as e:
            print(f"⚠️ Error getting learning recommendation: {e}")
            return {"message": "Learning path optimization temporarily unavailable"}
    
    def analyze_user_progress(self, user_progress: List[Dict]) -> Dict:
        """
        Analyze user progress to determine quiz strategy
        """
        if not user_progress:
            return {"strategy": "balanced", "topics": [], "difficulties": []}
        
        # Calculate overall performance
        total_attempts = sum(p.get('attempts', 0) for p in user_progress)
        total_correct = sum(p.get('correct', 0) for p in user_progress)
        overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        print(f"📊 Progress Analysis:")
        print(f"   Total attempts: {total_attempts}")
        print(f"   Total correct: {total_correct}")
        print(f"   Overall accuracy: {overall_accuracy}%")
        
        # Group by topic and difficulty
        topic_performance = {}
        for progress in user_progress:
            topic = progress.get('topic', 'Unknown')
            difficulty = progress.get('difficulty', 'medium')
            accuracy = progress.get('accuracy', 0)
            
            if topic not in topic_performance:
                topic_performance[topic] = {'easy': 0, 'medium': 0, 'hard': 0, 'total_accuracy': 0}
            
            topic_performance[topic][difficulty] = accuracy
        
        # Calculate total accuracy for each topic properly
        for topic in topic_performance:
            topic_data = topic_performance[topic]
            difficulties_with_attempts = [acc for acc in [topic_data['easy'], topic_data['medium'], topic_data['hard']] if acc > 0]
            
            if difficulties_with_attempts:
                topic_data['total_accuracy'] = sum(difficulties_with_attempts) / len(difficulties_with_attempts)
            else:
                topic_data['total_accuracy'] = 0
        
        # Determine strategy with smart progression logic
        if overall_accuracy < 50:
            strategy = "remedial"  # Focus on easy questions
            print(f"🎯 Low accuracy ({overall_accuracy}%) - using remedial strategy")
        elif overall_accuracy < 75:
            # Check if user is stuck in easy questions or has gaps
            easy_heavy = self._is_user_easy_heavy(topic_performance)
            has_gaps = self._has_significant_gaps(topic_performance)
            
            if easy_heavy and has_gaps:
                strategy = "exploration"  # Help user progress to harder difficulties
                print(f"🎯 Balanced accuracy ({overall_accuracy}%) but easy-heavy with gaps - using exploration strategy")
            else:
                strategy = "balanced"   # Mix of difficulties
                print(f"🎯 Balanced accuracy ({overall_accuracy}%) - using balanced strategy")
        else:
            # Advanced users need variety - check if they're missing difficulties
            missing_difficulties = []
            for topic in topic_performance:
                topic_data = topic_performance[topic]
                if topic_data['easy'] == 0:
                    missing_difficulties.append('easy')
                if topic_data['medium'] == 0:
                    missing_difficulties.append('medium')
                if topic_data['hard'] == 0:
                    missing_difficulties.append('hard')
            
            if missing_difficulties:
                strategy = "exploration"  # New strategy for variety
                print(f"🎯 High accuracy ({overall_accuracy}%) but missing difficulties: {missing_difficulties} - using exploration strategy")
            else:
                strategy = "advanced"     # True advanced - all difficulties attempted
                print(f"🎯 High accuracy ({overall_accuracy}%) with all difficulties attempted - using advanced strategy")
        
        print(f"📊 Final strategy: {strategy}")
        
        return {
            "strategy": strategy,
            "overall_accuracy": round(overall_accuracy, 2),
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "topic_performance": topic_performance,
            "topics": list(topic_performance.keys()),
            "difficulties": ["easy", "medium", "hard"]
        }
    
    def _is_user_easy_heavy(self, topic_performance: Dict) -> bool:
        """
        Check if user is mostly attempting easy questions
        """
        total_easy_attempts = 0
        total_medium_attempts = 0
        total_hard_attempts = 0
        
        for topic_data in topic_performance.values():
            # Count attempts based on accuracy > 0 (indicating attempts were made)
            if topic_data['easy'] > 0:
                total_easy_attempts += 1
            if topic_data['medium'] > 0:
                total_medium_attempts += 1
            if topic_data['hard'] > 0:
                total_hard_attempts += 1
        
        # User is easy-heavy if they have significantly more easy attempts than medium/hard
        total_attempts = total_easy_attempts + total_medium_attempts + total_hard_attempts
        if total_attempts == 0:
            return False
            
        easy_ratio = total_easy_attempts / total_attempts
        return easy_ratio > 0.6  # More than 60% of attempts are easy
    
    def _has_significant_gaps(self, topic_performance: Dict) -> bool:
        """
        Check if user has significant gaps in difficulty levels or topics
        """
        # Check for topics with 0% performance (no attempts)
        topics_with_no_attempts = 0
        total_topics = len(topic_performance)
        
        for topic_data in topic_performance.values():
            if topic_data['total_accuracy'] == 0:
                topics_with_no_attempts += 1
        
        # Check for difficulty gaps
        difficulty_coverage = {'easy': 0, 'medium': 0, 'hard': 0}
        for topic_data in topic_performance.values():
            for difficulty in ['easy', 'medium', 'hard']:
                if topic_data[difficulty] > 0:
                    difficulty_coverage[difficulty] += 1
        
        # User has gaps if:
        # 1. More than 25% of topics have no attempts, OR
        # 2. They haven't attempted medium or hard difficulties in most topics
        topic_gap_ratio = topics_with_no_attempts / total_topics if total_topics > 0 else 0
        has_difficulty_gaps = difficulty_coverage['medium'] < total_topics * 0.5 or difficulty_coverage['hard'] < total_topics * 0.3
        
        return topic_gap_ratio > 0.25 or has_difficulty_gaps
    
    def build_adaptive_filter(self, progress_analysis: Dict, topic_requests: List = None) -> Dict:
        """
        Build vector DB query filter based on user progress analysis
        Handles both Pydantic TopicRequest objects and dictionaries
        """
        strategy = progress_analysis.get("strategy", "balanced")
        
        # Handle topic_requests if provided
        if topic_requests and len(topic_requests) > 0:
            print(f"🎯 Using topic_requests structure: {topic_requests}")
            # Build specific filters based on user's topic and difficulty preferences
            filter_config = self._build_topic_specific_filter(topic_requests)
            return filter_config
        
        # No specific topic requests - use system's adaptive logic based on user progress
        print("🎯 No topic requests - using adaptive system logic")
        
        # Get topics from user's progress or available topics
        if progress_analysis.get("topics"):
            # Use user's existing topics but also add variety from other available topics
            user_topics = progress_analysis.get("topics", [])
            all_available_topics = self.get_all_available_topics()
            
            # Mix user's topics with other available topics for variety
            other_topics = [t for t in all_available_topics if t not in user_topics]
            # Take up to 2 additional topics for variety
            additional_topics = other_topics[:2] if other_topics else []
            topics = user_topics + additional_topics
        else:
            # No user progress, get all available topics
            topics = self.get_all_available_topics()
        
        # Ensure we have topics to work with
        if not topics:
            print("⚠️ No topics available - this should not happen")
            topics = ["Current Affairs"]  # Minimal fallback only if everything fails
        
        # Build filter based on strategy
        if strategy == "cold_start":
            # Cold start: easy questions across all available topics
            print("🎯 Cold start strategy: Easy questions across all topics")
            all_topics = self.get_all_available_topics()
            filter_config = {
                "should": [
                    {
                        "must": [
                            {"key": "topic", "match": {"value": topic}},
                            {"key": "difficulty", "match": {"value": "Easy"}}
                        ]
                    } for topic in all_topics
                ]
            }
        elif strategy == "remedial":
            # Focus on easy questions for struggling users
            filter_config = {
                "should": [
                    {
                        "must": [
                            {"key": "topic", "match": {"value": topic}},
                            {"key": "difficulty", "match": {"value": "Easy"}}
                        ]
                    } for topic in topics
                ]
            }
        elif strategy == "exploration":
            # Exploration strategy: focus on missing difficulties and new topics
            # Add topic rotation for more variety
            import time
            current_hour = int(time.time() / 3600) % 24  # Hour of day for rotation
            
            # Get all available topics dynamically
            all_available_topics = self.get_all_available_topics()
            
            # Create dynamic topic combinations (avoid hardcoded topics)
            if len(all_available_topics) >= 2:
                # Create rotating pairs from available topics
                topic_pairs = []
                for i in range(0, len(all_available_topics), 2):
                    if i + 1 < len(all_available_topics):
                        topic_pairs.append([all_available_topics[i], all_available_topics[i + 1]])
                    else:
                        topic_pairs.append([all_available_topics[i]])
                
                # Select topic pair based on current hour for variety
                selected_new_topics = topic_pairs[current_hour % len(topic_pairs)]
                print(f"🔄 Dynamic topic rotation: Hour {current_hour}, Selected: {selected_new_topics}")
            else:
                # Fallback if not enough topics
                selected_new_topics = all_available_topics[:2] if all_available_topics else []
                print(f"⚠️ Limited topics available: {selected_new_topics}")
            
            filter_config = {
                "should": [
                    # First priority: missing difficulties in existing topics
                    {
                        "must": [
                            {"key": "topic", "match": {"value": topic}},
                            {"key": "difficulty", "match": {"value": "Easy"}}
                        ]
                    } for topic in topics
                ] + [
                    {
                        "must": [
                            {"key": "topic", "match": {"value": topic}},
                            {"key": "difficulty", "match": {"value": "Hard"}}
                        ]
                    } for topic in topics
                ] + [
                    # Second priority: rotating new topics with easy difficulty
                    {
                        "must": [
                            {"key": "topic", "match": {"value": topic}},
                            {"key": "difficulty", "match": {"value": "Easy"}}
                        ]
                    } for topic in selected_new_topics
                ]
            }
        elif strategy == "advanced":
            # True advanced: all difficulties attempted, focus on challenging questions
            filter_config = {
                "should": [
                    {
                        "must": [
                            {"key": "topic", "match": {"value": topic}},
                            {"key": "difficulty", "match": {"value": "Hard"}}
                        ]
                    } for topic in topics
                ] + [
                    {
                        "must": [
                            {"key": "topic", "match": {"value": topic}},
                            {"key": "difficulty", "match": {"value": "Medium"}}
                        ]
                    } for topic in topics
                ]
            }
        else:
            # Balanced approach - mix of difficulties
            difficulties = ["Easy", "Medium", "Hard"]
            filter_config = {
                "should": [
                    {
                        "must": [
                            {"key": "topic", "match": {"value": topic}},
                            {"key": "difficulty", "match": {"value": difficulty}}
                        ]
                    } for topic in topics for difficulty in difficulties
                ]
            }
        
        return filter_config
    
    def _build_topic_specific_filter(self, topic_requests: List) -> Dict:
        """
        Build filter based on specific topic and difficulty requests from user
        Handles both Pydantic TopicRequest objects and dictionaries
        """
        print(f"🎯 Building topic-specific filter for {len(topic_requests)} requests")
        
        filter_conditions = []
        
        for topic_req in topic_requests:
            # Handle both Pydantic objects and dictionaries
            if hasattr(topic_req, 'topic'):
                # Pydantic object
                topic = topic_req.topic
                difficulty = topic_req.difficulty
            else:
                # Dictionary
                topic = topic_req.get("topic")
                difficulty = topic_req.get("difficulty")
            
            if not topic:
                continue
                
            if difficulty:
                # User specified both topic and difficulty
                print(f"🎯 Adding filter for topic: {topic}, difficulty: {difficulty}")
                filter_conditions.append({
                    "must": [
                        {"key": "topic", "match": {"value": topic}},
                        {"key": "difficulty", "match": {"value": difficulty}}
                    ]
                })
            else:
                # User only specified topic, system will choose difficulty
                print(f"🎯 Adding filter for topic: {topic} (any difficulty)")
                filter_conditions.append({
                    "must": [
                        {"key": "topic", "match": {"value": topic}}
                    ]
                })
        
        if not filter_conditions:
            print("⚠️ No valid topic requests found, falling back to default")
            return self._build_default_filter()
        
        print(f"🎯 Built {len(filter_conditions)} filter conditions")
        return {
            "should": filter_conditions
        }
    
    def _build_default_filter(self) -> Dict:
        """
        Build a default filter when no specific preferences are given
        """
        print("🎯 Building default filter")
        return {
            "should": [
                {
                    "must": [
                        {"key": "difficulty", "match": {"value": "Easy"}}
                    ]
                }
            ]
        }
    
    def get_all_available_topics(self) -> List[str]:
        """
        Dynamically fetch all available topics from the vector database
        """
        try:
            from src.vector_store.qdrant_utils import qdrant_client
            
            # Get a sample of questions to extract unique topics
            response = qdrant_client.scroll(
                collection_name="gktoday_questions",
                scroll_filter={},  # No filter to get all
                limit=1000,  # Get more to ensure we cover all topics
                with_payload=True
            )
            
            if not response or not response[0]:
                print("⚠️ No questions found in vector DB")
                return []  # Return empty list - let the system handle it gracefully
            
            # Extract unique topics from the questions
            topics = set()
            for question in response[0]:
                if hasattr(question, 'payload'):
                    topic = question.payload.get('topic')
                else:
                    topic = question.get('payload', {}).get('topic')
                
                if topic:
                    topics.add(topic)
            
            # Convert to list and sort for consistency
            topic_list = sorted(list(topics))
            print(f"🎯 Found {len(topic_list)} available topics: {topic_list}")
            
            return topic_list
            
        except Exception as e:
            print(f"❌ Error fetching available topics: {e}")
            # Fallback to empty list - let the system handle it gracefully
            return []
    
    def fetch_questions_from_vector_db(self, filter_config: Dict, limit: int, user_id: str = None) -> List[Dict]:
        """
        Fetch questions from Qdrant vector database using the adaptive filter
        """
        try:
            from src.vector_store.qdrant_utils import qdrant_client
            import random
            
            # Convert our filter to Qdrant format
            qdrant_filter = self.convert_filter_to_qdrant(filter_config)
            
            # Fetch more questions than needed to allow for deduplication
            fetch_limit = min(limit * 3, 100)  # Fetch up to 3x more, max 100
            
            # Fetch questions from Qdrant with offset for variety
            # Use timestamp-based offset to get different questions each time
            import time
            offset = int(time.time() * 1000) % 10000  # Use milliseconds timestamp as offset
            
            response = qdrant_client.scroll(
                collection_name="gktoday_questions",
                scroll_filter=qdrant_filter,
                limit=fetch_limit,
                offset=offset,  # Add offset for variety
                with_payload=True
            )
            
            questions = response[0] if response else []
            
            if not questions:
                return []
            
            # Remove duplicates based on question content
            unique_questions = self.remove_duplicate_questions(questions)
            
            # Shuffle questions for variety
            random.shuffle(unique_questions)
            
            print(f"🎲 Question variety: Fetched {len(questions)}, Unique: {len(unique_questions)}, Returning: {min(limit, len(unique_questions))}")
            
            # Return only the requested number of questions
            return unique_questions[:limit]
            
        except Exception as e:
            print(f"❌ Error fetching from vector DB: {e}")
            return []
    
    def remove_duplicate_questions(self, questions: List[Dict]) -> List[Dict]:
        """
        Remove duplicate questions based on question content
        """
        seen_questions = set()
        unique_questions = []
        
        for question in questions:
            # Handle Qdrant Record objects
            if hasattr(question, 'payload'):
                question_text = question.payload.get('question', '')
            else:
                question_text = question.get('payload', {}).get('question', '')
            
            # Create a normalized version for comparison (lowercase, no extra spaces)
            normalized_text = ' '.join(question_text.lower().split())
            
            if normalized_text not in seen_questions:
                seen_questions.add(normalized_text)
                unique_questions.append(question)
        
        print(f"🔄 Deduplication: {len(questions)} → {len(unique_questions)} unique questions")
        return unique_questions
    
    def convert_filter_to_qdrant(self, filter_config: Dict) -> Dict:
        """
        Convert our filter format to Qdrant's filter format
        """
        # This is a simplified conversion - you may need to adjust based on your Qdrant setup
        return filter_config
    
    def format_questions_for_quiz(self, questions: List[Dict]) -> List[Dict]:
        """
        Format vector DB questions for quiz response
        """
        formatted_questions = []
        
        for q in questions:
            # Handle Qdrant Record objects - they have .payload attribute
            if hasattr(q, 'payload'):
                payload = q.payload
                question_id = q.id
            else:
                # Fallback for dictionary format
                payload = q.get('payload', {})
                question_id = q.get('id', '')
            
            # Extract options (assuming they're stored as option_a, option_b, etc.)
            options = []
            for i in range(4):  # A, B, C, D
                option_key = f"option_{chr(97 + i)}"  # a, b, c, d
                if option_key in payload:
                    options.append(payload[option_key])
            
            formatted_questions.append({
                "id": str(question_id),
                "question": payload.get('question', ''),
                "options": options,
                "correct_answer": payload.get('answer', ''),
                "topic": payload.get('topic', 'Unknown'),
                "difficulty": payload.get('difficulty', 'medium'),
                "explanation": payload.get('notes', '')
            })
        
        return formatted_questions

# Global instance
adaptive_quiz_service = AdaptiveQuizService() 