#!/usr/bin/env python3
"""
Test script for RAGAS evaluation in the /quiz-detail endpoint

This script demonstrates the new RAGAS evaluation capabilities:
- Context Precision: Measures internet search result quality
- Faithfulness: Measures grounding in search results
- Answer Correctness: Measures factual accuracy
- Context Relevancy: Measures search result alignment
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_quiz_detail_without_evaluation():
    """Test quiz-detail endpoint without RAGAS evaluation"""
    
    print("🔍 Testing /quiz-detail endpoint WITHOUT RAGAS evaluation")
    print("=" * 70)
    
    payload = {
        "query": "What is machine learning?",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": False  # No evaluation
    }
    
    try:
        response = requests.post(f"{BASE_URL}/quiz-detail", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quiz-detail request successful!")
            print(f"Response keys: {list(result.keys())}")
            
            # Check that evaluation is not present
            if "evaluation" in result:
                print(f"❌ Evaluation present when not requested: {result['evaluation']}")
            else:
                print("✅ No evaluation data (as expected)")
                
        else:
            print(f"❌ Quiz-detail request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_quiz_detail_with_evaluation():
    """Test quiz-detail endpoint with RAGAS evaluation"""
    
    print("\n🔍 Testing /quiz-detail endpoint WITH RAGAS evaluation")
    print("=" * 70)
    
    payload = {
        "query": "What is machine learning?",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": True,  # Enable evaluation
        "ground_truth": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed."  # Optional ground truth
    }
    
    try:
        response = requests.post(f"{BASE_URL}/quiz-detail", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quiz-detail request successful!")
            print(f"Response keys: {list(result.keys())}")
            
            # Check evaluation data
            if "evaluation" in result and result["evaluation"]:
                evaluation = result["evaluation"]
                print("\n📊 RAGAS Evaluation Results:")
                print("-" * 40)
                
                if "error" in evaluation:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
                else:
                    # Display metrics
                    metrics = evaluation.get("metrics", {})
                    print(f"🎯 Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"🔒 Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
                    print(f"✅ Answer Correctness: {metrics.get('answer_correctness', 'N/A'):.3f}")
                    print(f"🎯 Context Relevancy: {metrics.get('context_relevancy', 'N/A'):.3f}")
                    print(f"🌟 Overall Score: {metrics.get('overall_score', 'N/A'):.3f}")
                    
                    # Display quality insights
                    insights = evaluation.get("quality_insights", {})
                    if insights:
                        print("\n💡 Quality Insights:")
                        for metric, insight in insights.items():
                            print(f"  • {metric.replace('_', ' ').title()}: {insight}")
                    
                    # Display recommendations
                    recommendations = evaluation.get("recommendations", [])
                    if recommendations:
                        print("\n🚀 Recommendations:")
                        for i, rec in enumerate(recommendations, 1):
                            print(f"  {i}. {rec}")
                    
                    # Display metadata
                    metadata = evaluation.get("metadata", {})
                    if metadata:
                        print(f"\n📋 Metadata: {metadata}")
                        
            else:
                print("❌ No evaluation data found")
                
        else:
            print(f"❌ Quiz-detail request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_quiz_detail_with_evaluation_no_ground_truth():
    """Test quiz-detail endpoint with RAGAS evaluation but no ground truth"""
    
    print("\n🔍 Testing /quiz-detail endpoint WITH RAGAS evaluation (no ground truth)")
    print("=" * 70)
    
    payload = {
        "query": "Explain quantum computing",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": True,  # Enable evaluation
        # No ground truth provided
    }
    
    try:
        response = requests.post(f"{BASE_URL}/quiz-detail", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quiz-detail request successful!")
            
            # Check evaluation data
            if "evaluation" in result and result["evaluation"]:
                evaluation = result["evaluation"]
                
                if "error" in evaluation:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
                else:
                    metrics = evaluation.get("metrics", {})
                    metadata = evaluation.get("metadata", {})
                    
                    print(f"🎯 Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"🔒 Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
                    print(f"✅ Answer Correctness: {metrics.get('answer_correctness', 'N/A'):.3f}")
                    print(f"🎯 Context Relevancy: {metrics.get('context_relevancy', 'N/A'):.3f}")
                    print(f"🌟 Overall Score: {metrics.get('overall_score', 'N/A'):.3f}")
                    
                    print(f"\n📋 Ground Truth Provided: {metadata.get('ground_truth_provided', False)}")
                    
            else:
                print("❌ No evaluation data found")
                
        else:
            print(f"❌ Quiz-detail request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_different_quiz_queries():
    """Test different types of quiz queries with evaluation"""
    
    print("\n🔍 Testing different quiz query types with RAGAS evaluation")
    print("=" * 70)
    
    test_queries = [
        "What are the benefits of renewable energy?",
        "Explain the concept of blockchain technology",
        "How does photosynthesis work?",
        "What is the history of the internet?"
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
            response = requests.post(f"{BASE_URL}/quiz-detail", json=payload)
            
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
                    print(f"   Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"   Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
                else:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
            else:
                print(f"❌ Quiz-detail request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(1)

def compare_query_vs_quiz_detail():
    """Compare evaluation results between /query and /quiz-detail endpoints"""
    
    print("\n🔍 Comparing /query vs /quiz-detail evaluation results")
    print("=" * 70)
    
    test_query = "What is artificial intelligence?"
    
    # Test /query endpoint
    print("🔄 Testing /query endpoint...")
    query_payload = {
        "query": test_query,
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": True
    }
    
    try:
        query_response = requests.post(f"{BASE_URL}/query", json=query_payload)
        if query_response.status_code == 200:
            query_result = query_response.json()
            query_evaluation = query_result.get("evaluation", {})
            
            if "error" not in query_evaluation:
                query_metrics = query_evaluation.get("metrics", {})
                print(f"✅ /query Overall Score: {query_metrics.get('overall_score', 'N/A'):.3f}")
            else:
                print(f"❌ /query evaluation failed: {query_evaluation['error']}")
        else:
            print(f"❌ /query request failed: {query_response.status_code}")
    except Exception as e:
        print(f"❌ /query request failed: {e}")
    
    # Test /quiz-detail endpoint
    print("\n🔄 Testing /quiz-detail endpoint...")
    quiz_payload = {
        "query": test_query,
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": True
    }
    
    try:
        quiz_response = requests.post(f"{BASE_URL}/quiz-detail", json=quiz_payload)
        if quiz_response.status_code == 200:
            quiz_result = quiz_response.json()
            quiz_evaluation = quiz_result.get("evaluation", {})
            
            if "error" not in quiz_evaluation:
                quiz_metrics = quiz_evaluation.get("metrics", {})
                print(f"✅ /quiz-detail Overall Score: {quiz_metrics.get('overall_score', 'N/A'):.3f}")
            else:
                print(f"❌ /quiz-detail evaluation failed: {quiz_evaluation['error']}")
        else:
            print(f"❌ /quiz-detail request failed: {quiz_response.status_code}")
    except Exception as e:
        print(f"❌ /quiz-detail request failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Quiz-Detail RAGAS Evaluation Test Suite")
    print("=" * 70)
    print("This test suite demonstrates the new RAGAS evaluation capabilities")
    print("in the /quiz-detail endpoint, providing comprehensive quality metrics")
    print("for internet search results and LLM-enhanced responses.")
    print()
    
    # Test 1: Without evaluation
    test_quiz_detail_without_evaluation()
    
    # Test 2: With evaluation and ground truth
    test_quiz_detail_with_evaluation()
    
    # Test 3: With evaluation but no ground truth
    test_quiz_detail_with_evaluation_no_ground_truth()
    
    # Test 4: Different query types
    test_different_quiz_queries()
    
    # Test 5: Compare endpoints
    compare_query_vs_quiz_detail()
    
    print("\n" + "=" * 70)
    print("✅ Quiz-Detail RAGAS Evaluation Test Suite Complete!")
    print("\n📊 Key Metrics for Quiz-Detail:")
    print("• Context Precision: How well internet search finds relevant results")
    print("• Faithfulness: How well LLM summary is grounded in search results")
    print("• Answer Correctness: Factual accuracy of search-based responses")
    print("• Context Relevancy: How well search results align with query intent")
    print("\n💡 Use these metrics to:")
    print("  - Validate internet search quality")
    print("  - Assess LLM enhancement effectiveness")
    print("  - Compare with vector search performance")
    print("  - Optimize search and reranking strategies")

if __name__ == "__main__":
    main() 