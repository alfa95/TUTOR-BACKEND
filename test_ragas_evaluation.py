#!/usr/bin/env python3
"""
Test script for RAGAS evaluation in the /query endpoint

This script demonstrates the new RAGAS evaluation capabilities:
- Context Precision: Measures retriever quality
- Faithfulness: Measures grounding in context
- Answer Correctness: Measures factual accuracy
- Context Relevancy: Measures recommendation alignment
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_query_without_evaluation():
    """Test query endpoint without RAGAS evaluation"""
    
    print("🔍 Testing /query endpoint WITHOUT RAGAS evaluation")
    print("=" * 60)
    
    payload = {
        "query": "What is machine learning?",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": False  # No evaluation
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful!")
            print(f"Response keys: {list(result.keys())}")
            
            # Check that evaluation is not present
            if "evaluation" in result:
                print(f"❌ Evaluation present when not requested: {result['evaluation']}")
            else:
                print("✅ No evaluation data (as expected)")
                
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_query_with_evaluation():
    """Test query endpoint with RAGAS evaluation"""
    
    print("\n🔍 Testing /query endpoint WITH RAGAS evaluation")
    print("=" * 60)
    
    payload = {
        "query": "What is machine learning?",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": True,  # Enable evaluation
        "ground_truth": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."  # Optional ground truth
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful!")
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
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_query_with_evaluation_no_ground_truth():
    """Test query endpoint with RAGAS evaluation but no ground truth"""
    
    print("\n🔍 Testing /query endpoint WITH RAGAS evaluation (no ground truth)")
    print("=" * 60)
    
    payload = {
        "query": "Explain quantum computing",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": True,  # Enable evaluation
        # No ground truth provided
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful!")
            
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
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_different_queries():
    """Test different types of queries with evaluation"""
    
    print("\n🔍 Testing different query types with RAGAS evaluation")
    print("=" * 60)
    
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
            response = requests.post(f"{BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                evaluation = result.get("evaluation", {})
                
                if "error" not in evaluation:
                    metrics = evaluation.get("metrics", {})
                    overall_score = metrics.get('overall_score', 0.0)
                    
                    # Color code the score
                    if overall_score >= 0.8:
                        score_emoji = "🟢"
                    elif overall_score >= 0.6:
                        score_emoji = "🟡"
                    else:
                        score_emoji = "🔴"
                    
                    print(f"{score_emoji} Overall Score: {overall_score:.3f}")
                    print(f"   Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"   Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
                else:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
            else:
                print(f"❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(1)

def main():
    """Run all tests"""
    print("🚀 RAGAS Evaluation Test Suite")
    print("=" * 60)
    print("This test suite demonstrates the new RAGAS evaluation capabilities")
    print("in the /query endpoint, providing comprehensive RAG quality metrics.")
    print()
    
    # Test 1: Without evaluation
    test_query_without_evaluation()
    
    # Test 2: With evaluation and ground truth
    test_query_with_evaluation()
    
    # Test 3: With evaluation but no ground truth
    test_query_with_evaluation_no_ground_truth()
    
    # Test 4: Different query types
    test_different_queries()
    
    print("\n" + "=" * 60)
    print("✅ RAGAS Evaluation Test Suite Complete!")
    print("\n📊 Key Metrics Explained:")
    print("• Context Precision: How well the retriever finds relevant context")
    print("• Faithfulness: How well responses are grounded in retrieved context")
    print("• Answer Correctness: Factual accuracy of generated responses")
    print("• Context Relevancy: How well recommendations align with user intent")
    print("\n💡 Use these metrics to:")
    print("  - Identify retriever issues (low context precision)")
    print("  - Detect hallucination (low faithfulness)")
    print("  - Validate answer quality (low answer correctness)")
    print("  - Optimize recommendations (low context relevancy)")

if __name__ == "__main__":
    main() 