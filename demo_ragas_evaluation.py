#!/usr/bin/env python3
"""
Simple demo script for RAGAS evaluation in the query endpoint
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def demo_ragas_evaluation():
    """Demonstrate RAGAS evaluation functionality"""
    
    print("🚀 RAGAS Evaluation Demo")
    print("=" * 50)
    
    # Test query with evaluation enabled
    payload = {
        "query": "What is artificial intelligence?",
        "use_llm": True,
        "enable_reranking": True,
        "reranking_strategy": "semantic_relevance",
        "enable_evaluation": True,  # Enable RAGAS evaluation
        "ground_truth": "Artificial intelligence is the simulation of human intelligence in machines that are programmed to think and learn like humans."
    }
    
    print(f"📝 Query: {payload['query']}")
    print(f"🔍 Evaluation: {'Enabled' if payload['enable_evaluation'] else 'Disabled'}")
    print(f"📚 Ground Truth: {'Provided' if payload['ground_truth'] else 'Not provided'}")
    print()
    
    try:
        print("🔄 Sending request...")
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print()
            
            # Check if evaluation data is present
            if "evaluation" in result and result["evaluation"]:
                evaluation = result["evaluation"]
                
                if "error" in evaluation:
                    print(f"❌ Evaluation failed: {evaluation['error']}")
                else:
                    print("📊 RAGAS Evaluation Results:")
                    print("-" * 30)
                    
                    # Display metrics
                    metrics = evaluation.get("metrics", {})
                    print(f"🎯 Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"🔒 Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
                    print(f"✅ Answer Correctness: {metrics.get('answer_correctness', 'N/A'):.3f}")
                    print(f"🎯 Context Relevancy: {metrics.get('context_relevancy', 'N/A'):.3f}")
                    print(f"🌟 Overall Score: {metrics.get('overall_score', 'N/A'):.3f}")
                    
                    # Display insights
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
            else:
                print("❌ No evaluation data found in response")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Demo complete! Check the metrics above to understand")
    print("your RAG system's performance across all dimensions.")

if __name__ == "__main__":
    demo_ragas_evaluation() 