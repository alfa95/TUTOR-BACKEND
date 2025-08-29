"""
Adaptive Quiz Service - Handles user progress analysis and question recommendation
"""
from typing import List, Dict, Optional
from fastapi import HTTPException
from src.db.supabase_utils import get_user_topic_progress

class AdaptiveQuizService:
    def __init__(self):
        pass
    
    def get_adaptive_quiz_questions(
        self, 
        jwt_token: str, 
        num_questions: int = 10, 
        topics: List[str] = None
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
            
            # Step 4: Build vector DB query filter based on progress
            if progress_analysis.get("is_new_user"):
                print("🎯 New user - building cold start filter")
                vector_filter = self.build_adaptive_filter(progress_analysis, None)  # No topics needed for cold start
            else:
                print(f"🎯 Building filter for topics: {topics}")
                vector_filter = self.build_adaptive_filter(progress_analysis, topics)
            print(f"🎯 Vector filter: {vector_filter}")
            
            # Step 5: Fetch questions from vector database
            print(f"🔍 Calling vector DB with filter: {vector_filter}")
            questions = self.fetch_questions_from_vector_db(vector_filter, num_questions)
            print(f"📚 Fetched {len(questions)} questions from vector DB")
            print(f"📋 Raw questions data: {questions[:2] if questions else 'No questions'}")
            
            # Step 6: Format response
            quiz_questions = self.format_questions_for_quiz(questions)
            
            return {
                "user_id": user_id,
                "progress_summary": progress_analysis,
                "recommended_questions": quiz_questions,
                "quiz_strategy": progress_analysis.get("strategy", "balanced"),
                "is_new_user": progress_analysis.get("is_new_user", False)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error in adaptive quiz service: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate adaptive quiz: {str(e)}")
    
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
        elif overall_accuracy < 75:
            strategy = "balanced"   # Mix of difficulties
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
                print(f"🎯 User missing difficulties: {missing_difficulties} - using exploration strategy")
            else:
                strategy = "advanced"     # True advanced - all difficulties attempted
                print(f"🎯 User has attempted all difficulties - using advanced strategy")
        
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
    
    def build_adaptive_filter(self, progress_analysis: Dict, requested_topics: List[str] = None) -> Dict:
        """
        Build vector DB query filter based on user progress analysis
        """
        strategy = progress_analysis.get("strategy", "balanced")
        
        # Get topics dynamically from vector DB if none requested
        if requested_topics:
            topics = requested_topics
        elif progress_analysis.get("topics"):
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
                    # Second priority: new topics with easy difficulty for confidence
                    {
                        "must": [
                            {"key": "topic", "match": {"value": "Geography"}},
                            {"key": "difficulty", "match": {"value": "Easy"}}
                        ]
                    },
                    {
                        "must": [
                            {"key": "topic", "match": {"value": "History"}},
                            {"key": "difficulty", "match": {"value": "Easy"}}
                        ]
                    }
                ]
            }
        elif strategy == "advanced":
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
                return ["Current Affairs"]  # Fallback
            
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
            # Fallback to common topics
            return ["Current Affairs", "Geography", "History", "Economy"]
    
    def fetch_questions_from_vector_db(self, filter_config: Dict, limit: int) -> List[Dict]:
        """
        Fetch questions from Qdrant vector database using the adaptive filter
        """
        try:
            from src.vector_store.qdrant_utils import qdrant_client
            
            # Convert our filter to Qdrant format
            qdrant_filter = self.convert_filter_to_qdrant(filter_config)
            
            # Fetch questions from Qdrant
            response = qdrant_client.scroll(
                collection_name="gktoday_questions",
                scroll_filter=qdrant_filter,
                limit=limit,
                with_payload=True
            )
            
            return response[0] if response else []
            
        except Exception as e:
            print(f"❌ Error fetching from vector DB: {e}")
            return []
    
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