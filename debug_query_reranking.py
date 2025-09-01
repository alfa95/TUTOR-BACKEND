#!/usr/bin/env python3
"""
Debug script to test query endpoint reranking step by step
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_query_step_by_step():
    """Test query endpoint step by step to identify the issue"""
    
    print("🔍 Debugging Query Endpoint Reranking Step by Step")
    print("=" * 60)
    
    # Test 1: Query without reranking (should work)
    print("\n1️⃣ Testing WITHOUT reranking (baseline)")
    print("-" * 40)
    
    payload_no_rerank = {
        "query": "What is machine learning?",
        "use_llm": False,
        "enable_reranking": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload_no_rerank)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ No reranking: SUCCESS")
            print(f"Response keys: {list(result.keys())}")
            
            response_data = result.get("response", {})
            print(f"Response data keys: {list(response_data.keys())}")
            
            questions = response_data.get("questions", [])
            print(f"Number of questions: {len(questions)}")
            
            if questions:
                print("Sample question:")
                print(f"  - {questions[0]}")
        else:
            print(f"❌ No reranking: FAILED - {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ No reranking: ERROR - {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Query with reranking (should work but currently failing)
    print("\n2️⃣ Testing WITH reranking (currently failing)")
    print("-" * 40)
    
    payload_with_rerank = {
        "query": "What is machine learning?",
        "use_llm": False,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload_with_rerank)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ With reranking: SUCCESS")
            print(f"Response keys: {list(result.keys())}")
            
            response_data = result.get("response", {})
            print(f"Response data keys: {list(response_data.keys())}")
            
            questions = response_data.get("questions", [])
            print(f"Number of questions: {len(questions)}")
            
            if questions:
                print("Sample question:")
                print(f"  - {questions[0]}")
            else:
                print("⚠️ No questions found in response!")
                
        else:
            print(f"❌ With reranking: FAILED - {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ With reranking: ERROR - {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Check server logs (if possible)
    print("\n3️⃣ Checking for server-side issues")
    print("-" * 40)
    print("Check your server console for:")
    print("  - 🔍 Converting X results for reranking")
    print("  - 🔍 Reranking returned X results")
    print("  - ✅ Mapped position X to result")
    print("  - ⚠️ Reranking produced no results")
    print("  - ❌ Reranking failed")
    
    print("\n" + "=" * 60)
    
    # Test 4: Test reranking service directly
    print("\n4️⃣ Testing reranking service directly")
    print("-" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/debug/reranking")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Debug reranking: SUCCESS")
            print(f"Reranking service working: {result}")
        else:
            print(f"❌ Debug reranking: FAILED - {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Debug reranking: ERROR - {e}")

def test_simple_queries():
    """Test with very simple queries to isolate the issue"""
    
    print("\n🔍 Testing with Simple Queries")
    print("=" * 40)
    
    simple_queries = [
        "test",
        "hello",
        "simple query"
    ]
    
    for query in simple_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 20)
        
        # Without reranking
        payload_no_rerank = {
            "query": query,
            "use_llm": False,
            "enable_reranking": False
        }
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=payload_no_rerank)
            if response.status_code == 200:
                result = response.json()
                questions = result.get("response", {}).get("questions", [])
                print(f"  No reranking: {len(questions)} results")
            else:
                print(f"  No reranking: FAILED")
        except Exception as e:
            print(f"  No reranking: ERROR - {e}")
        
        # With reranking
        payload_with_rerank = {
            "query": query,
            "use_llm": False,
            "enable_reranking": True,
            "reranking_strategy": "semantic_relevance"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=payload_with_rerank)
            if response.status_code == 200:
                result = response.json()
                questions = result.get("response", {}).get("questions", [])
                print(f"  With reranking: {len(questions)} results")
            else:
                print(f"  With reranking: FAILED")
        except Exception as e:
            print(f"  With reranking: ERROR - {e}")

def main():
    """Run all debug tests"""
    
    print("🚀 Query Endpoint Reranking Debug Tool")
    print("=" * 70)
    
    # Test step by step
    test_query_step_by_step()
    
    # Test simple queries
    test_simple_queries()
    
    print("\n" + "=" * 70)
    print("🏁 Debug testing completed!")
    print("\n📋 Next Steps:")
    print("1. Check server console for error messages")
    print("2. Verify reranking service is working")
    print("3. Check if context is being passed correctly")
    print("4. Ensure SearchResult conversion is working")

if __name__ == "__main__":
    main() 