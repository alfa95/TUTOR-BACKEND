#!/usr/bin/env python3
"""
Demo script showing dynamic metrics generation from actual system performance
"""

import requests
import time
import json
from datetime import datetime

# API configuration
BASE_URL = "http://localhost:8000"

def demo_dynamic_metrics():
    """Demonstrate how metrics are generated from actual API calls"""
    
    print("🚀 Dynamic Metrics Demo - Real System Performance")
    print("=" * 60)
    print("This demo shows how metrics are generated from actual API usage")
    print()
    
    # Step 1: Show initial metrics (should be low/zero)
    print("📊 Step 1: Initial Metrics (No API calls yet)")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/dashboard", timeout=10)
        if response.status_code == 200:
            metrics = response.json()
            print(f"   Retrieval Accuracy: {metrics['retrieval_accuracy']['with_llm_reranking']}")
            print(f"   Response Time: {metrics['response_time']['with_llm_explanations']}s")
            print(f"   Total API Calls: {metrics.get('total_api_calls', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Step 2: Make some API calls to generate metrics
    print("📡 Step 2: Making API Calls to Generate Metrics")
    print("-" * 50)
    
    test_queries = [
        {"query": "What is artificial intelligence?", "use_llm": False},
        {"query": "Explain machine learning", "use_llm": True},
        {"query": "How does neural networks work?", "use_llm": False},
        {"query": "Deep learning applications", "use_llm": True},
        {"query": "AI in healthcare", "use_llm": False}
    ]
    
    for i, query_data in enumerate(test_queries, 1):
        print(f"   📝 API Call {i}: {query_data['query'][:30]}...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/quiz-detail",
                json=query_data,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"      ✅ Success ({response_time:.2f}s)")
            else:
                print(f"      ❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Failed: {e}")
        
        # Small delay between calls
        time.sleep(0.5)
    
    print()
    
    # Step 3: Show updated metrics after API calls
    print("📊 Step 3: Updated Metrics (After API Calls)")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/dashboard", timeout=10)
        if response.status_code == 200:
            metrics = response.json()
            print(f"   Retrieval Accuracy: {metrics['retrieval_accuracy']['with_llm_reranking']}")
            print(f"   Response Time (with LLM): {metrics['response_time']['with_llm_explanations']}s")
            print(f"   Response Time (without LLM): {metrics['response_time']['without_llm']}s")
            print(f"   LLM Overhead: {metrics['response_time']['overhead']}s")
            print(f"   Quality Score: {metrics['explanation_relevance']['explanation_relevance']}/5")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Step 4: Show real-time system status
    print("🔄 Step 4: Real-Time System Status")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/realtime", timeout=10)
        if response.status_code == 200:
            realtime = response.json()
            print(f"   System Status: {realtime['status']}")
            print(f"   Current Load: {realtime['current_load']}")
            print(f"   Active Connections: {realtime['active_connections']}")
            print(f"   Memory Usage: {realtime['memory_usage']}")
            print(f"   CPU Usage: {realtime['cpu_usage']}")
            print(f"   Uptime: {realtime['uptime']}")
            print(f"   Total API Calls: {realtime['total_api_calls']}")
            print(f"   Success Rate: {realtime['success_rate']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Step 5: Show performance summary with insights
    print("📋 Step 5: Performance Summary & Insights")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/summary", timeout=10)
        if response.status_code == 200:
            summary = response.json()
            print(f"   Overall Score: {summary['overall_score']}/100")
            print(f"   Top Performing Area: {summary['top_performing_area']}")
            
            if summary['areas_for_improvement']:
                print(f"   Areas for Improvement:")
                for area in summary['areas_for_improvement']:
                    print(f"      • {area}")
            
            if summary['recommendations']:
                print(f"   Recommendations:")
                for rec in summary['recommendations']:
                    print(f"      • {rec}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Step 6: Show performance trends
    print("📈 Step 6: Performance Trends (Last 7 Days)")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/trends?days=7", timeout=10)
        if response.status_code == 200:
            trends_data = response.json()
            print(f"   Trends for last {trends_data['period_days']} days:")
            
            for trend in trends_data['trends'][:3]:  # Show first 3 days
                print(f"      📅 {trend['date']}:")
                print(f"         Retrieval Accuracy: {trend['retrieval_accuracy']}")
                print(f"         Response Time: {trend['response_time']}s")
                print(f"         Quality: {trend['explanation_relevance']}/5")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Main demo function"""
    
    print("🎯 Dynamic Metrics System Demonstration")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target API: {BASE_URL}")
    print()
    
    print("💡 What This Demo Shows:")
    print("   1. Initial metrics (zero/empty)")
    print("   2. Making actual API calls")
    print("   3. Metrics updating in real-time")
    print("   4. System performance insights")
    print("   5. Performance trends")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running! Starting demo...")
            print()
            demo_dynamic_metrics()
        else:
            print("❌ Server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("   Please start your server with: uvicorn src.api.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("🏁 Demo completed!")
    print()
    print("💡 Key Benefits of Dynamic Metrics:")
    print("   • Real-time performance monitoring")
    print("   • Actual system data, not hardcoded values")
    print("   • Automatic trend analysis")
    print("   • Performance insights and recommendations")
    print("   • System health monitoring")

if __name__ == "__main__":
    main() 