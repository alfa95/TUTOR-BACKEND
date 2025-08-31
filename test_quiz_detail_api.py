#!/usr/bin/env python3
"""
Test script for the quiz-detail API endpoint
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = "/quiz-detail"

def test_quiz_detail_api():
    """Test the quiz-detail API endpoint"""
    
    # Test data
    test_queries = [
        "What is the capital of France?",
        "Who invented the telephone?",
        "What is the largest planet in our solar system?",
        "When was the first moon landing?"
    ]
    
    print("🧪 Testing Quiz Detail API Endpoint")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        
        # Prepare request payload
        payload = {
            "query": query,
            "use_llm": False  # Set to True to test LLM enhancement
        }
        
        try:
            # Make API request
            response = requests.post(
                f"{BASE_URL}{API_ENDPOINT}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Found {result.get('total_results', 0)} results")
                
                # Display first result
                if result.get('results') and len(result['results']) > 0:
                    first_result = result['results'][0]
                    print(f"   📰 Title: {first_result.get('title', 'N/A')}")
                    print(f"   🔗 URL: {first_result.get('link', 'N/A')}")
                    print(f"   📝 Snippet: {first_result.get('snippet', 'N/A')[:100]}...")
                
                # Show LLM summary if available
                if result.get('llm_summary'):
                    print(f"   🤖 LLM Summary: {result['llm_summary'][:150]}...")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

def test_with_llm_enhancement():
    """Test the API with LLM enhancement enabled"""
    
    print("\n🧠 Testing with LLM Enhancement")
    print("=" * 50)
    
    payload = {
        "query": "What are the main causes of climate change?",
        "use_llm": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_ENDPOINT}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for LLM processing
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Found {result.get('total_results', 0)} results")
            
            if result.get('llm_summary'):
                print(f"\n🤖 LLM Summary:")
                print(result['llm_summary'])
            else:
                print("⚠️ No LLM summary generated")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if SERPERDEV_API_KEY is set
    if not os.getenv("SERPERDEV_API_KEY"):
        print("⚠️  SERPERDEV_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        exit(1)
    
    # Run tests
    test_quiz_detail_api()
    test_with_llm_enhancement() 