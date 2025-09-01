#!/usr/bin/env python3
"""
Test script for the System Metrics API endpoints
"""

import requests
import json
from datetime import datetime

# API configuration
BASE_URL = "http://localhost:8000"

def test_metrics_dashboard():
    """Test the main metrics dashboard endpoint"""
    
    print("📊 Testing System Metrics Dashboard")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/dashboard", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Metrics Dashboard Retrieved Successfully!")
            
            # Display key metrics
            print(f"\n🎯 Retrieval Accuracy:")
            print(f"   With LLM + Re-ranking: {metrics['retrieval_accuracy']['with_llm_reranking']}")
            print(f"   Retrieval-only: {metrics['retrieval_accuracy']['retrieval_only']}")
            print(f"   Improvement: {metrics['retrieval_accuracy']['improvement']}%")
            
            print(f"\n📈 Recall:")
            print(f"   With LLM: {metrics['recall']['with_llm']}")
            print(f"   Retrieval-only: {metrics['recall']['retrieval_only']}")
            print(f"   Improvement: {metrics['recall']['improvement']}%")
            
            print(f"\n⏱️ Response Time:")
            print(f"   With LLM explanations: {metrics['response_time']['with_llm_explanations']}s")
            print(f"   Without LLM: {metrics['response_time']['without_llm']}s")
            print(f"   Overhead: {metrics['response_time']['overhead']}s")
            
            print(f"\n⭐ Explanation Relevance:")
            print(f"   Score: {metrics['explanation_relevance']['explanation_relevance']}/5")
            print(f"   Human Reviewers: {metrics['explanation_relevance']['human_reviewers']}")
            
            print(f"\n🧪 Test Coverage:")
            print(f"   Coverage: {metrics['test_coverage']['coverage_percentage']}%")
            
            print(f"\n📅 Last Updated: {metrics['last_updated']}")
            print(f"🔧 System Version: {metrics['system_version']}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_metrics_summary():
    """Test the metrics summary endpoint"""
    
    print("\n📋 Testing Metrics Summary")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/summary", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            summary = response.json()
            print("✅ Metrics Summary Retrieved Successfully!")
            
            print(f"\n🏆 Overall Score: {summary['overall_score']}/100")
            print(f"🌟 Top Performing Area: {summary['top_performing_area']}")
            
            if summary['areas_for_improvement']:
                print(f"\n⚠️ Areas for Improvement:")
                for area in summary['areas_for_improvement']:
                    print(f"   • {area}")
            
            if summary['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in summary['recommendations']:
                    print(f"   • {rec}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_performance_trends():
    """Test the performance trends endpoint"""
    
    print("\n📈 Testing Performance Trends")
    print("=" * 50)
    
    try:
        # Test with 7 days
        response = requests.get(f"{BASE_URL}/metrics/trends?days=7", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            trends_data = response.json()
            print("✅ Performance Trends Retrieved Successfully!")
            
            print(f"📊 Trends for last {trends_data['period_days']} days:")
            
            for trend in trends_data['trends'][:3]:  # Show first 3 days
                print(f"\n📅 {trend['date']}:")
                print(f"   Retrieval Accuracy: {trend['retrieval_accuracy']}")
                print(f"   Recall: {trend['recall']}")
                print(f"   Response Time: {trend['response_time']}s")
                print(f"   Explanation Relevance: {trend['explanation_relevance']}/5")
            
            if len(trends_data['trends']) > 3:
                print(f"\n... and {len(trends_data['trends']) - 3} more days")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_real_time_metrics():
    """Test the real-time metrics endpoint"""
    
    print("\n🔄 Testing Real-Time Metrics")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/metrics/realtime", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            realtime = response.json()
            print("✅ Real-Time Metrics Retrieved Successfully!")
            
            print(f"\n💻 System Status: {realtime['status']}")
            print(f"📊 Current Load: {realtime['current_load']}")
            print(f"🔗 Active Connections: {realtime['active_connections']}")
            print(f"💾 Memory Usage: {realtime['memory_usage']}")
            print(f"⚡ CPU Usage: {realtime['cpu_usage']}")
            print(f"⏰ Uptime: {realtime['uptime']}")
            
            if realtime['last_error']:
                print(f"❌ Last Error: {realtime['last_error']}")
            else:
                print("✅ No recent errors")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    
    print("🚀 System Metrics API Testing")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    test_metrics_dashboard()
    test_metrics_summary()
    test_performance_trends()
    test_real_time_metrics()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!")
    print("\n💡 Available Metrics Endpoints:")
    print("   • GET /metrics/dashboard - Comprehensive metrics")
    print("   • GET /metrics/summary - Performance summary with insights")
    print("   • GET /metrics/trends?days=30 - Performance trends")
    print("   • GET /metrics/realtime - Real-time system status")

if __name__ == "__main__":
    main() 