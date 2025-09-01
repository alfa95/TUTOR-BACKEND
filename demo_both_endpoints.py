#!/usr/bin/env python3
"""
Demo script showing RAGAS evaluation in both /query and /quiz-detail endpoints

This demonstrates the unified evaluation system across different data sources:
- /query: Vector database search with educational content
- /quiz-detail: Internet search with real-time results
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def demo_query_endpoint():
    """Demonstrate RAGAS evaluation in /query endpoint"""
    
    print("🔍 Demo: /query Endpoint with RAGAS Evaluation")
    print("=" * 60)
    
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
        print("🔄 Sending request to /query...")
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ /query request successful!")
            
            # Display evaluation results
            if "evaluation" in result and result["evaluation"]:
                evaluation = result["evaluation"]
                
                if "error" not in evaluation:
                    metrics = evaluation.get("metrics", {})
                    print(f"\n📊 /query Evaluation Results:")
                    print(f"  🎯 Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"  🔒 Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
                    print(f"  ✅ Answer Correctness: {metrics.get('answer_correctness', 'N/A'):.3f}")
                    print(f"  🎯 Context Relevancy: {metrics.get('context_relevancy', 'N/A'):.3f}")
                    print(f"  🌟 Overall Score: {metrics.get('overall_score', 'N/A'):.3f}")
                    
                    # Show insights
                    insights = evaluation.get("quality_insights", {})
                    if insights:
                        print(f"\n💡 Key Insight:")
                        for metric, insight in list(insights.items())[:1]:  # Show first insight
                            print(f"  • {insight}")
                else:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
            else:
                print("❌ No evaluation data found")
                
        else:
            print(f"❌ /query request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ /query request failed: {e}")
    
    print("\n" + "=" * 60)

def demo_quiz_detail_endpoint():
    """Demonstrate RAGAS evaluation in /quiz-detail endpoint"""
    
    print("🔍 Demo: /quiz-detail Endpoint with RAGAS Evaluation")
    print("=" * 60)
    
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
        print("🔄 Sending request to /quiz-detail...")
        response = requests.post(f"{BASE_URL}/quiz-detail", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ /quiz-detail request successful!")
            
            # Display evaluation results
            if "evaluation" in result and result["evaluation"]:
                evaluation = result["evaluation"]
                
                if "error" not in evaluation:
                    metrics = evaluation.get("metrics", {})
                    print(f"\n📊 /quiz-detail Evaluation Results:")
                    print(f"  🎯 Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"  🔒 Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
                    print(f"  ✅ Answer Correctness: {metrics.get('answer_correctness', 'N/A'):.3f}")
                    print(f"  🎯 Context Relevancy: {metrics.get('context_relevancy', 'N/A'):.3f}")
                    print(f"  🌟 Overall Score: {metrics.get('overall_score', 'N/A'):.3f}")
                    
                    # Show insights
                    insights = evaluation.get("quality_insights", {})
                    if insights:
                        print(f"\n💡 Key Insight:")
                        for metric, insight in list(insights.items())[:1]:  # Show first insight
                            print(f"  • {insight}")
                else:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
            else:
                print("❌ No evaluation data found")
                
        else:
            print(f"❌ /quiz-detail request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ /quiz-detail request failed: {e}")
    
    print("\n" + "=" * 60)

def compare_endpoints():
    """Compare evaluation results between both endpoints"""
    
    print("🔍 Demo: Comparing Both Endpoints")
    print("=" * 60)
    
    test_query = "What is artificial intelligence?"
    
    print(f"📝 Test Query: {test_query}")
    print("🔄 Testing both endpoints with same query...")
    print()
    
    # Test /query endpoint
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
                print(f"✅ /query Endpoint:")
                print(f"  🌟 Overall Score: {query_metrics.get('overall_score', 'N/A'):.3f}")
                print(f"  🎯 Context Precision: {query_metrics.get('context_precision', 'N/A'):.3f}")
                print(f"  🔒 Faithfulness: {query_metrics.get('faithfulness', 'N/A'):.3f}")
            else:
                print(f"❌ /query evaluation failed: {query_evaluation['error']}")
        else:
            print(f"❌ /query request failed: {query_response.status_code}")
    except Exception as e:
        print(f"❌ /query request failed: {e}")
    
    print()
    
    # Test /quiz-detail endpoint
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
                print(f"✅ /quiz-detail Endpoint:")
                print(f"  🌟 Overall Score: {quiz_metrics.get('overall_score', 'N/A'):.3f}")
                print(f"  🎯 Context Precision: {quiz_metrics.get('context_precision', 'N/A'):.3f}")
                print(f"  🔒 Faithfulness: {quiz_metrics.get('faithfulness', 'N/A'):.3f}")
            else:
                print(f"❌ /quiz-detail evaluation failed: {quiz_evaluation['error']}")
        else:
            print(f"❌ /quiz-detail request failed: {quiz_response.status_code}")
    except Exception as e:
        print(f"❌ /quiz-detail request failed: {e}")
    
    print("\n" + "=" * 60)

def main():
    """Run the complete demo"""
    print("🚀 RAGAS Evaluation Demo - Both Endpoints")
    print("=" * 60)
    print("This demo shows RAGAS evaluation working in both endpoints:")
    print("• /query: Vector database search with educational content")
    print("• /quiz-detail: Internet search with real-time results")
    print()
    
    # Demo 1: Query endpoint
    demo_query_endpoint()
    
    # Demo 2: Quiz-detail endpoint
    demo_quiz_detail_endpoint()
    
    # Demo 3: Comparison
    compare_endpoints()
    
    print("🎯 Demo Complete!")
    print("\n💡 Key Benefits of Unified Evaluation:")
    print("  • Consistent quality metrics across all data sources")
    print("  • Same lenient rules for real-world applications")
    print("  • Comprehensive system monitoring and optimization")
    print("  • Data-driven improvements for both search strategies")
    print("\n🚀 Your RAG system now has complete quality visibility!")

if __name__ == "__main__":
    main() 