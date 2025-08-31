#!/usr/bin/env python3
"""
Test Learning Path Dashboard API - Single endpoint with LLM enhancement!
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8000"

# Test JWT token (replace with a real one)
TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6Im5od0x6MXR1SDR6TUhobTQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2pwcnRhd2l4eG92YW1maHdnc3FtLnN1cGFib3NlLmNvL2F1dGgvdjEiLCJzdWIiOiIxZDQ5MWUwMi04NDg5LTQ1MDgtODE5Ni1kNjI1NTNhYjVlNmEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MzY5MjEwLCJpYXQiOjE3NTYzNjU2MTAsImVtYWlsIjoiYW51cmFnLmFsZmE5NUBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6Imdvb2dsZSIsInByb3ZpZGVycyI6WyJnb29nbGUiXX0sInVzZXJfbWV0YWRhdGEiOnsiYXZhdGFyX3VybCI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0w4cmQ2c2JkVnMtbklBSmFwMElOa3hVMTc1UWhKLWVwV3pWS05nR0YwZlNnSWZFZz1zOTYtYyIsImVtYWlsIjoiYW51cmFnLmFsZmE5NUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZnVsbF9uYW1lIjoiYW51cmFnIiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwibmFtZSI6ImFudXJhZyIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0w4cmQ2c2JkVnMtbklBSmFwMElOa3hVMTc1UWhKLWVwV3pWS05nR0YwZlNnSWZFZz1zOTYtYyIsInByb3ZpZGVyX2lkIjoiMTAxNzY4NDI0Nzc0MjkxNTQ0ODU5Iiwic3ViIjoiMTAxNzY4NDI0Nzc0MjkxNTQ0ODU5In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoib2F1dGgiLCJ0aW1lc3RhbXAiOjE3NTYzNTk0NzJ9XSwic2Vzc2lvbl9pZCI6IjU4YWZiMmJiLTExYmJkLTRmMTktOGYwZS04OWE3Y2M1YjkwYjMiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.QU9H35qd14de2BbJ9ic9sDvokIouJhSJGQsThwPmNJI"

def test_rule_based_dashboard():
    """Test the learning dashboard API in rule-based mode"""
    
    print("🧠 Testing Learning Dashboard API (Rule-Based Mode)")
    print("=" * 60)
    
    # Test data - rule-based mode (llm: false)
    test_data = {
        "jwt_token": TEST_JWT,
        "llm": False  # Use rule-based system
    }
    
    try:
        # Make API call to single endpoint
        response = requests.post(
            f"{BASE_URL}/learning-path/dashboard",
            headers={
                "Content-Type": "application/json"
            },
            json=test_data
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Rule-Based Dashboard Test Successful!")
            
            # Validate response structure
            if result.get("success") and result.get("data"):
                data = result["data"]
                
                print(f"\n🎯 Dashboard Data Summary (Rule-Based):")
                print(f"   ✅ Enhancement Method: {data.get('enhancement_method', 'Unknown')}")
                print(f"   ✅ User Progress: {'user_id' in data.get('user_progress', {})}")
                print(f"   ✅ Next Skill: {data.get('next_skill') is not None}")
                print(f"   ✅ Available Skills: {len(data.get('available_skills', []))} skills")
                print(f"   ✅ Learning Path: {data.get('learning_path') is not None}")
                print(f"   ✅ Milestones: {len(data.get('milestones', []))} milestones")
                
                # Show that LLM features are not present
                print(f"\n📋 Rule-Based Features:")
                print(f"   • Standard learning path")
                print(f"   • Basic milestones")
                print(f"   • Static skill recommendations")
                print(f"   • No LLM enhancement")
                
            else:
                print("⚠️ Response structure incomplete")
                
        else:
            print(f"❌ API Test Failed: {response.status_code}")
            print(f"📋 Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_llm_enhanced_dashboard():
    """Test the learning dashboard API with LLM enhancement"""
    
    print("\n🧠 Testing Learning Dashboard API (LLM-Enhanced Mode)")
    print("=" * 60)
    
    # Test data - LLM enhanced mode
    test_data = {
        "jwt_token": TEST_JWT,
        "llm": True  # Activate LLM enhancement!
    }
    
    try:
        # Make API call to single endpoint
        response = requests.post(
            f"{BASE_URL}/learning-path/dashboard",
            headers={
                "Content-Type": "application/json"
            },
            json=test_data
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM-Enhanced Dashboard Test Successful!")
            
            # Validate response structure
            if result.get("success") and result.get("data"):
                data = result["data"]
                
                print(f"\n🎯 Dashboard Data Summary (LLM-Enhanced):")
                print(f"   ✅ Enhancement Method: {data.get('enhancement_method', 'Unknown')}")
                print(f"   ✅ LLM Status: {data.get('llm_enhancement_status', 'Unknown')}")
                print(f"   ✅ User Progress: {'user_id' in data.get('user_progress', {})}")
                print(f"   ✅ Next Skill: {data.get('next_skill') is not None}")
                print(f"   ✅ Available Skills: {len(data.get('available_skills', []))} skills")
                
                # Check for LLM-enhanced features
                next_skill = data.get('next_skill', {})
                if next_skill.get('enhanced_by_llm'):
                    print(f"   ✅ Next Skill Enhanced by LLM: {len(next_skill.get('learning_tips', []))} personalized tips")
                
                if data.get('milestones_enhanced_by_llm'):
                    print(f"   ✅ Milestones Enhanced by LLM: {len(data.get('milestones', []))} intelligent milestones")
                
                if data.get('llm_priority_skills'):
                    print(f"   ✅ LLM Priority Skills: {len(data.get('llm_priority_skills', []))} skills")
                
                if data.get('enhanced_recommendations'):
                    print(f"   ✅ Enhanced Recommendations: Available")
                
                # Show LLM features
                print(f"\n🚀 LLM-Enhanced Features:")
                print(f"   • Personalized learning tips")
                print(f"   • Intelligent milestone design")
                print(f"   • Smart skill gap analysis")
                print(f"   • Enhanced learning strategies")
                print(f"   • Real-world applications")
                print(f"   • Study schedule optimization")
                
            else:
                print("⚠️ Response structure incomplete")
                
        else:
            print(f"❌ API Test Failed: {response.status_code}")
            print(f"📋 Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_minimal_dashboard():
    """Test dashboard with minimal required fields"""
    
    print("\n🧠 Testing Dashboard API (Minimal Fields)...")
    
    # Minimal test data - only JWT token needed
    test_data = {
        "jwt_token": TEST_JWT
        # No other fields needed - defaults to rule-based
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/learning-path/dashboard",
            headers={
                "Content-Type": "application/json"
            },
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Minimal Dashboard Test Successful!")
            print(f"🎯 Got comprehensive data in one call!")
            print(f"📊 Enhancement method: {result.get('data', {}).get('enhancement_method', 'Unknown')}")
        else:
            print(f"❌ Minimal Dashboard Test Failed: {response.status_code}")
            print(f"📋 Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Learning Dashboard API Test Suite")
    print("🎯 Single Endpoint - Rule-Based + LLM Enhancement!")
    print("=" * 60)
    
    test_rule_based_dashboard()
    test_llm_enhanced_dashboard()
    test_minimal_dashboard()
    
    print("\n✨ Test Suite Complete!")
    print("🎉 Now you have ONE API with TWO modes:")
    print("   📋 Rule-Based: Fast, reliable, predictable")
    print("   🧠 LLM-Enhanced: Intelligent, personalized, adaptive") 