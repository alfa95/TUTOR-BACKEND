"""
Supabase utilities for user topic progress
"""
import os
from typing import Dict, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_anon_key)
    
    def get_user_topic_progress(self, user_id: str) -> List[Dict]:
        """
        Get user topic progress for a specific user
        """
        try:
            response = self.client.table('user_topic_progress').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching user topic progress for {user_id}: {e}")
            return []
    
    def get_user_topic_difficulty_progress(self, user_id: str, topic: str, difficulty: str) -> Optional[Dict]:
        """
        Get user progress for a specific topic and difficulty level
        """
        try:
            response = self.client.table('user_topic_progress').select('*').eq('user_id', user_id).eq('topic', topic).eq('difficulty', difficulty).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching progress for {user_id}, {topic}, {difficulty}: {e}")
            return None
    
    def get_user_topic_summary(self, user_id: str, topic: str) -> Dict:
        """
        Get summary of user progress across all difficulty levels for a topic
        """
        try:
            response = self.client.table('user_topic_progress').select('*').eq('user_id', user_id).eq('topic', topic).execute()
            progress_data = response.data
            
            if not progress_data:
                return {
                    "user_id": user_id,
                    "topic": topic,
                    "total_attempts": 0,
                    "total_correct": 0,
                    "overall_accuracy": 0.0,
                    "difficulty_breakdown": {}
                }
            
            total_attempts = sum(p.get('attempts', 0) for p in progress_data)
            total_correct = sum(p.get('correct', 0) for p in progress_data)
            overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0
            
            difficulty_breakdown = {}
            for p in progress_data:
                diff = p.get('difficulty', 'unknown')
                difficulty_breakdown[diff] = {
                    "attempts": p.get('attempts', 0),
                    "correct": p.get('correct', 0),
                    "accuracy": p.get('accuracy', 0.0)
                }
            
            return {
                "user_id": user_id,
                "topic": topic,
                "total_attempts": total_attempts,
                "total_correct": total_correct,
                "overall_accuracy": round(overall_accuracy, 2),
                "difficulty_breakdown": difficulty_breakdown
            }
        except Exception as e:
            print(f"Error fetching topic summary for {user_id}, {topic}: {e}")
            return {"user_id": user_id, "topic": topic, "error": str(e)}
    
    def get_user_topic_progress_authenticated(self, user_id: str, jwt_token: str) -> List[Dict]:
        """
        Get user topic progress using JWT authentication
        """
        try:
            # Create a new client with the user's JWT token
            from supabase import create_client
            auth_client = create_client(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_ANON_KEY')
            )
            
            # Set the user's JWT token for authentication
            auth_client.auth.set_session(jwt_token, None)
            
            # Now query with user context
            response = auth_client.table('user_topic_progress').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching authenticated user topic progress for {user_id}: {e}")
            return []

# Global instance - will be created when first accessed
_supabase_manager = None

def get_supabase_manager():
    """Get or create SupabaseManager instance"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager

# Convenience function
def get_user_topic_progress(user_id: str) -> List[Dict]:
    """Get user topic progress for a specific user"""
    manager = get_supabase_manager()
    return manager.get_user_topic_progress(user_id)

def get_user_topic_difficulty_progress(user_id: str, topic: str, difficulty: str) -> Optional[Dict]:
    """Get user progress for a specific topic and difficulty level"""
    manager = get_supabase_manager()
    return manager.get_user_topic_difficulty_progress(user_id, topic, difficulty)

def get_user_topic_summary(user_id: str, topic: str) -> Dict:
    """Get summary of user progress across all difficulty levels for a topic"""
    manager = get_supabase_manager()
    return manager.get_user_topic_summary(user_id, topic)

def get_user_topic_progress_authenticated(user_id: str, jwt_token: str) -> List[Dict]:
    """Get user topic progress using JWT authentication"""
    manager = get_supabase_manager()
    return manager.get_user_topic_progress_authenticated(user_id, jwt_token) 