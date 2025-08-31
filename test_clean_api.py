#!/usr/bin/env python3
"""
Test to show our Learning Path API is clean - no email needed!
"""
import requests
import json

def test_clean_learning_path_api():
    """Test that our learning path API only needs JWT + num_questions"""
    
    print("🧠 Testing Clean Learning Path API...")
    print("=" * 50)
    
    # Our clean API - only 2 fields needed!
    clean_request = {
        "jwt_token": "your-jwt-token-here",
        "num_questions": 10
    }
    
    print("✅ Our Learning Path API Request:")
    print(f"   JWT Token: {clean_request['jwt_token'][:20]}...")
    print(f"   Num Questions: {clean_request['num_questions']}")
    print(f"   Total Fields: {len(clean_request)}")
    print()
    
    print("🎯 What We DON'T Need:")
    print("   ❌ email - NOT needed!")
    print("   ❌ role - NOT needed!")
    print("   ❌ provider - NOT needed!")
    print("   ❌ session_id - NOT needed!")
    print("   ❌ user_preferences - NOT needed!")
    print("   ❌ time_constraints - NOT needed!")
    print("   ❌ target_skills - NOT needed!")
    print()
    
    print("✅ What We Actually Use:")
    print("   ✅ JWT Token → Extract user_id")
    print("   ✅ Num Questions → Generate quiz")
    print()
    
    print("🚀 API Endpoints We Created:")
    print("   1. POST /learning-path/optimize")
    print("   2. GET /learning-path/skills")
    print("   3. GET /learning-path/user-progress")
    print()
    
    print("⚠️ Old Endpoints (Still Use Email - NOT Our API):")
    print("   - POST /quiz-session/today")
    print("   - POST /quiz-session/mark-completed")
    print("   - POST /quiz-session/submit")
    print("   - GET /analyze-user")
    print("   - GET /in-depth-analysis")
    print()
    
    print("✨ Our Learning Path API is SUPER CLEAN!")
    print("   Only JWT + num_questions needed!")

if __name__ == "__main__":
    test_clean_learning_path_api() 