#!/usr/bin/env python3
"""
Test script for the enhanced /query endpoint with reranking
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_query_without_reranking():
    """Test query endpoint without reranking"""
    
    print("🔍 Testing /query endpoint WITHOUT reranking")
    print("=" * 50)
    
    payload = {
        "query": "What is machine learning?",
        "use_llm": True,
        "enable_reranking": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_query_with_reranking():
    """Test query endpoint with reranking"""
    
    print("\n🚀 Testing /query endpoint WITH reranking")
    print("=" * 50)
    
    payload = {
        "query": "What is machine learning?",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query with reranking successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Query with reranking failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_query_with_different_strategies():
    """Test query endpoint with different reranking strategies"""
    
    strategies = ["semantic_relevance", "query_intent", "hybrid"]
    
    for strategy in strategies:
        print(f"\n🎯 Testing /query endpoint with {strategy} strategy")
        print("-" * 50)
        
        payload = {
            "query": "Explain artificial intelligence concepts",
            "use_llm": True,
            "enable_reranking": True,
            "reranking_strategy": strategy
        }
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {strategy} strategy successful!")
                
                # Extract context to show reranking results
                response_data = result.get("response", {})
                context = response_data.get("questions", [])
                
                if context:
                    print(f"Found {len(context)} results:")
                    for i, item in enumerate(context, 1):
                        title = item.get("question", "No title")[:50]
                        score = item.get("relevance_score", "N/A")
                        rerank_pos = item.get("rerank_position", "N/A")
                        print(f"  {i}. {title}...")
                        print(f"     Relevance Score: {score}")
                        print(f"     Rerank Position: {rerank_pos}")
                else:
                    print("No context results found")
                    
            else:
                print(f"❌ {strategy} strategy failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

def test_performance_comparison():
    """Compare performance with and without reranking"""
    
    print("\n⏱️ Performance Comparison: With vs Without Reranking")
    print("=" * 60)
    
    queries = [
        "What is machine learning?",
        "Explain neural networks",
        "How does deep learning work?",
        "What are the applications of AI?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        # Test without reranking
        start_time = time.time()
        payload_no_rerank = {
            "query": query,
            "use_llm": False,
            "enable_reranking": False
        }
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=payload_no_rerank)
            no_rerank_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"  Without Reranking: {no_rerank_time:.2f}s ✅")
            else:
                print(f"  Without Reranking: Failed ❌")
                
        except Exception as e:
            print(f"  Without Reranking: Error ❌")
            no_rerank_time = 0
        
        # Test with reranking
        start_time = time.time()
        payload_with_rerank = {
            "query": query,
            "use_llm": False,
            "enable_reranking": True,
            "reranking_strategy": "semantic_relevance"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=payload_with_rerank)
            with_rerank_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"  With Reranking: {with_rerank_time:.2f}s ✅")
                
                # Calculate overhead
                if no_rerank_time > 0:
                    overhead = ((with_rerank_time - no_rerank_time) / no_rerank_time) * 100
                    print(f"  Reranking Overhead: {overhead:+.1f}%")
                    
            else:
                print(f"  With Reranking: Failed ❌")
                
        except Exception as e:
            print(f"  With Reranking: Error ❌")

def main():
    """Run all tests"""
    
    print("🚀 Enhanced Query Endpoint with Reranking - Test Suite")
    print("=" * 70)
    
    # Test basic functionality
    test_query_without_reranking()
    test_query_with_reranking()
    
    # Test different strategies
    test_query_with_different_strategies()
    
    # Test performance
    test_performance_comparison()
    
    print("\n" + "=" * 70)
    print("🏁 All tests completed!")

if __name__ == "__main__":
    main() 