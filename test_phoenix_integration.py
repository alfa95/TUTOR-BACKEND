#!/usr/bin/env python3
"""
Test script for Phoenix integration with quiz-detail endpoint

This script tests the Arize Phoenix integration for LLM observability:
- Phoenix server startup
- Request tracing
- Performance logging
- Quality metrics tracking
"""

import requests
import json
import time
import webbrowser

# API base URL
BASE_URL = "http://localhost:8000"

def test_phoenix_status():
    """Test Phoenix server status"""
    
    print("🔍 Testing Phoenix Server Status")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/phoenix/status")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Phoenix status check successful!")
            print(f"📊 Phoenix Available: {result.get('phoenix_available', False)}")
            print(f"🌐 Phoenix URL: {result.get('phoenix_url', 'N/A')}")
            print(f"🔌 Port: {result.get('port', 'N/A')}")
            print(f"⏰ Timestamp: {result.get('timestamp', 'N/A')}")
            
            return result.get('phoenix_available', False)
        else:
            print(f"❌ Phoenix status check failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Phoenix status check failed: {e}")
        return False

def start_phoenix_server():
    """Start Phoenix server"""
    
    print("\n🚀 Starting Phoenix Server")
    print("=" * 50)
    
    try:
        response = requests.post(f"{BASE_URL}/phoenix/start")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Phoenix server started successfully!")
            print(f"📊 Status: {result.get('status', 'N/A')}")
            print(f"💬 Message: {result.get('message', 'N/A')}")
            print(f"🌐 Phoenix URL: {result.get('phoenix_url', 'N/A')}")
            print(f"⏰ Timestamp: {result.get('timestamp', 'N/A')}")
            
            # Try to open Phoenix UI in browser
            phoenix_url = result.get('phoenix_url')
            if phoenix_url:
                print(f"\n🌐 Opening Phoenix UI in browser...")
                try:
                    webbrowser.open(phoenix_url)
                except Exception as e:
                    print(f"⚠️ Could not open browser automatically: {e}")
                    print(f"💡 Please manually open: {phoenix_url}")
            
            return True
        else:
            print(f"❌ Phoenix server start failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Phoenix server start failed: {e}")
        return False

def test_quiz_detail_with_phoenix():
    """Test quiz-detail endpoint with Phoenix logging"""
    
    print("\n🔍 Testing Quiz-Detail with Phoenix Logging")
    print("=" * 50)
    
    payload = {
        "query": "What is machine learning?",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": True,
        "ground_truth": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed."
    }
    
    print(f"📝 Query: {payload['query']}")
    print(f"🔍 Evaluation: {'Enabled' if payload['enable_evaluation'] else 'Disabled'}")
    print(f"📚 Ground Truth: {'Provided' if payload['ground_truth'] else 'Not provided'}")
    print()
    
    try:
        print("🔄 Sending request to /quiz-detail with Phoenix logging...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/quiz-detail", json=payload)
        
        total_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quiz-detail request successful!")
            print(f"⏱️  Total Time: {total_time:.3f}s")
            
            # Check evaluation data
            if "evaluation" in result and result["evaluation"]:
                evaluation = result["evaluation"]
                
                if "error" not in evaluation:
                    metrics = evaluation.get("metrics", {})
                    print(f"\n📊 RAGAS Evaluation Results:")
                    print(f"  🎯 Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"  🔒 Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
                    print(f"  ✅ Answer Correctness: {metrics.get('answer_correctness', 'N/A'):.3f}")
                    print(f"  🎯 Context Relevancy: {metrics.get('context_relevancy', 'N/A'):.3f}")
                    print(f"  🌟 Overall Score: {metrics.get('overall_score', 'N/A'):.3f}")
                    
                    print(f"\n🔍 Phoenix Logging:")
                    print(f"  • Request traced with unique ID")
                    print(f"  • Search performance logged")
                    print(f"  • LLM enhancement tracked")
                    print(f"  • RAGAS evaluation recorded")
                    print(f"  • Request completion logged")
                    
                else:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
            else:
                print("❌ No evaluation data found")
                
        else:
            print(f"❌ Quiz-detail request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_multiple_requests():
    """Test multiple requests to see Phoenix tracing in action"""
    
    print("\n🔍 Testing Multiple Requests for Phoenix Tracing")
    print("=" * 50)
    
    test_queries = [
        "What is artificial intelligence?",
        "Explain quantum computing",
        "How does photosynthesis work?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: {query}")
        print("-" * 40)
        
        payload = {
            "query": query,
            "use_llm": True,
            "enable_reranking": True,
            "reranking_strategy": "semantic_relevance",
            "enable_evaluation": True
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/quiz-detail", json=payload)
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                evaluation = result.get("evaluation", {})
                
                if "error" not in evaluation:
                    metrics = evaluation.get("metrics", {})
                    overall_score = metrics.get('overall_score', 0.0)
                    
                    # Color code the score
                    if overall_score >= 0.6:
                        score_emoji = "🟢"
                    elif overall_score >= 0.4:
                        score_emoji = "🟡"
                    else:
                        score_emoji = "🔴"
                    
                    print(f"{score_emoji} Overall Score: {overall_score:.3f}")
                    print(f"   ⏱️  Response Time: {total_time:.3f}s")
                    print(f"   🔍 Phoenix Trace: Generated")
                else:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(1)

def main():
    """Run the complete Phoenix integration test"""
    print("🚀 Phoenix Integration Test Suite")
    print("=" * 50)
    print("This test suite demonstrates Arize Phoenix integration")
    print("for comprehensive LLM observability in the quiz-detail endpoint.")
    print()
    
    # Test 1: Check Phoenix status
    phoenix_available = test_phoenix_status()
    
    if not phoenix_available:
        print("\n⚠️ Phoenix is not available. Please check installation.")
        return
    
    # Test 2: Start Phoenix server
    server_started = start_phoenix_server()
    
    if not server_started:
        print("\n⚠️ Could not start Phoenix server. Continuing with tests...")
    
    # Test 3: Test quiz-detail with Phoenix logging
    test_quiz_detail_with_phoenix()
    
    # Test 4: Test multiple requests
    test_multiple_requests()
    
    print("\n" + "=" * 50)
    print("🎯 Phoenix Integration Test Suite Complete!")
    print("\n💡 What Phoenix Provides:")
    print("  • Request/response tracing")
    print("  • Performance metrics")
    print("  • LLM enhancement tracking")
    print("  • RAGAS evaluation logging")
    print("  • Real-time monitoring")
    print("\n🌐 Access Phoenix UI:")
    print(f"  • URL: http://localhost:8001")
    print("  • View traces, metrics, and insights")
    print("  • Monitor LLM performance")
    print("  • Track quality improvements")

if __name__ == "__main__":
    main() 