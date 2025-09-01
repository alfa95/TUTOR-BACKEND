#!/usr/bin/env python3
"""
Demo script showing how reranking improves search result relevance
"""

import requests
import json
from datetime import datetime

# API configuration
BASE_URL = "http://localhost:8000"

def demo_reranking_comparison():
    """Demonstrate the difference between regular search and reranked search"""
    
    print("🎯 Reranking Demo - Before vs After")
    print("=" * 60)
    
    # Test query that benefits from reranking
    test_query = "What is machine learning and how does it work?"
    
    print(f"🔍 Test Query: {test_query}")
    print()
    
    # Test 1: Regular search (no reranking)
    print("📊 Test 1: Regular Search (No Reranking)")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/quiz-detail",
            json={
                "query": test_query,
                "use_llm": False,
                "enable_reranking": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Regular search successful!")
            print(f"Results (in original order):")
            
            for i, result in enumerate(results.get('results', []), 1):
                print(f"  {i}. {result.get('title', 'N/A')[:60]}...")
                print(f"     Relevance: {result.get('relevance_score', 'N/A')}")
                print(f"     Position: {result.get('position', 'N/A')}")
                print()
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Reranked search
    print("🚀 Test 2: Reranked Search (Semantic Relevance)")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/quiz-detail",
            json={
                "query": test_query,
                "use_llm": False,
                "enable_reranking": True,
                "reranking_strategy": "semantic_relevance"
            },
            timeout=60  # Longer timeout for reranking
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Reranked search successful!")
            print(f"Results (reranked by relevance):")
            
            for i, result in enumerate(results.get('results', []), 1):
                print(f"  {i}. {result.get('title', 'N/A')[:60]}...")
                print(f"     Relevance Score: {result.get('relevance_score', 'N/A')}")
                print(f"     Original Position: {result.get('position', 'N/A')}")
                print(f"     Rerank Position: {result.get('rerank_position', 'N/A')}")
                print()
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

def demo_different_reranking_strategies():
    """Demonstrate different reranking strategies"""
    
    print("🔄 Different Reranking Strategies")
    print("=" * 60)
    
    test_query = "How to implement neural networks in Python?"
    
    strategies = [
        ("semantic_relevance", "Semantic Relevance"),
        ("query_intent", "Query Intent"),
        ("hybrid", "Hybrid (Semantic + Intent)")
    ]
    
    for strategy, strategy_name in strategies:
        print(f"🎯 Strategy: {strategy_name}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{BASE_URL}/quiz-detail",
                json={
                    "query": test_query,
                    "use_llm": False,
                    "enable_reranking": True,
                    "reranking_strategy": strategy
                },
                timeout=60
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ {strategy_name} reranking successful!")
                
                # Show top 2 results for comparison
                for i, result in enumerate(results.get('results', [])[:2], 1):
                    print(f"  {i}. {result.get('title', 'N/A')[:50]}...")
                    print(f"     Score: {result.get('relevance_score', 'N/A')}")
                    print(f"     Original: {result.get('position', 'N/A')} → Rerank: {result.get('rerank_position', 'N/A')}")
                    print()
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def demo_reranking_with_llm_enhancement():
    """Demonstrate reranking combined with LLM enhancement"""
    
    print("🧠 Reranking + LLM Enhancement")
    print("=" * 60)
    
    test_query = "Explain the difference between supervised and unsupervised learning"
    
    try:
        response = requests.post(
            f"{BASE_URL}/quiz-detail",
            json={
                "query": test_query,
                "use_llm": True,
                "enable_reranking": True,
                "reranking_strategy": "hybrid"
            },
            timeout=90  # Longest timeout for full processing
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Reranked + LLM enhanced search successful!")
            print()
            
            print("📊 Reranked Results:")
            for i, result in enumerate(results.get('results', []), 1):
                print(f"  {i}. {result.get('title', 'N/A')[:50]}...")
                print(f"     Relevance: {result.get('relevance_score', 'N/A')}")
                print()
            
            if results.get('llm_summary'):
                print("🤖 LLM Summary:")
                print(results['llm_summary'])
            else:
                print("⚠️ No LLM summary generated")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main demo function"""
    
    print("🚀 Reranking System Demonstration")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target API: {BASE_URL}")
    print()
    
    print("💡 What This Demo Shows:")
    print("   1. Regular search vs reranked search")
    print("   2. Different reranking strategies")
    print("   3. Reranking + LLM enhancement")
    print("   4. Relevance scores and position changes")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running! Starting reranking demo...")
            print()
            
            # Run all demos
            demo_reranking_comparison()
            demo_different_reranking_strategies()
            demo_reranking_with_llm_enhancement()
            
        else:
            print("❌ Server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("   Please start your server with: uvicorn src.api.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("🏁 Reranking demo completed!")
    print()
    print("💡 Key Benefits of Reranking:")
    print("   • Better result relevance")
    print("   • Improved user experience")
    print("   • Higher accuracy metrics")
    print("   • Context-aware ordering")
    print()
    print("🔧 Available Reranking Strategies:")
    print("   • semantic_relevance: Focus on content relevance")
    print("   • query_intent: Consider user's goal")
    print("   • hybrid: Combine both approaches")

if __name__ == "__main__":
    main() 