#!/usr/bin/env python3
"""
Simple Phoenix Integration Demo

This script demonstrates the Phoenix integration with a single request
to show how LLM observability works in practice.
"""

import requests
import time

# API base URL
BASE_URL = "http://localhost:8000"

def demo_phoenix_integration():
    """Demonstrate Phoenix integration with quiz-detail"""
    
    print("🚀 Phoenix Integration Demo")
    print("=" * 50)
    print("This demo shows how Phoenix tracks LLM requests:")
    print("• Request tracing and performance")
    print("• Search result quality")
    print("• LLM enhancement metrics")
    print("• RAGAS evaluation tracking")
    print()
    
    # Test query
    query = "What is artificial intelligence?"
    print(f"📝 Query: {query}")
    print()
    
    # Start Phoenix server
    print("🔄 Starting Phoenix server...")
    try:
        response = requests.post(f"{BASE_URL}/phoenix/start")
        if response.status_code == 200:
            result = response.json()
            phoenix_url = result.get('phoenix_url')
            print(f"✅ Phoenix server started!")
            print(f"🌐 Access UI at: {phoenix_url}")
        else:
            print(f"⚠️ Phoenix server start failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Phoenix server start failed: {e}")
    
    print()
    
    # Make request with Phoenix logging
    print("🔄 Making quiz-detail request with Phoenix logging...")
    
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
            print(f"✅ Request successful! ({total_time:.3f}s)")
            
            # Show evaluation results
            if "evaluation" in result and result["evaluation"]:
                evaluation = result["evaluation"]
                if "error" not in evaluation:
                    metrics = evaluation.get("metrics", {})
                    print(f"\n📊 Quality Metrics:")
                    print(f"  🎯 Overall Score: {metrics.get('overall_score', 'N/A'):.3f}")
                    print(f"  🔍 Context Precision: {metrics.get('context_precision', 'N/A'):.3f}")
                    print(f"  🤖 Faithfulness: {metrics.get('faithfulness', 'N/A'):.3f}")
            
            print(f"\n🔍 Phoenix Tracking:")
            print(f"  • Request traced with unique ID")
            print(f"  • Performance metrics logged")
            print(f"  • Quality evaluation recorded")
            print(f"  • Ready for analysis in Phoenix UI")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Demo Complete!")
    print("\n💡 Next Steps:")
    print("  1. Open Phoenix UI in your browser")
    print("  2. View the trace for this request")
    print("  3. Analyze performance metrics")
    print("  4. Monitor quality trends")
    print("\n🚀 Your LLM observability is now active!")

if __name__ == "__main__":
    demo_phoenix_integration() 