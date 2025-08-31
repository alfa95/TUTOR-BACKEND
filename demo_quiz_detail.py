#!/usr/bin/env python3
"""
Simple demonstration of the quiz-detail API functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def demo_internet_search():
    """Demonstrate the internet search functionality directly"""
    
    print("🔍 Demo: Internet Search Tool")
    print("=" * 40)
    
    # Check if API key is available
    if not os.getenv("SERPERDEV_API_KEY"):
        print("❌ SERPERDEV_API_KEY not found in environment variables")
        print("Please add it to your .env file")
        return
    
    try:
        from src.agents.internet_search_tools import search_internet
        
        # Test queries
        test_queries = [
            "What is artificial intelligence?",
            "Who was Albert Einstein?",
            "What is the speed of light?"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            print("-" * 30)
            
            results = search_internet(query, num_results=3)
            
            if results and not any("error" in str(r) for r in results):
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.get('title', 'N/A')}")
                    print(f"   URL: {result.get('link', 'N/A')}")
                    print(f"   Snippet: {result.get('snippet', 'N/A')[:80]}...")
                    print()
            else:
                print("❌ Search failed or returned errors")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_langgraph_agent():
    """Demonstrate the LangGraph agent functionality"""
    
    print("\n🧠 Demo: LangGraph Agent")
    print("=" * 40)
    
    try:
        from src.agents.internet_search_agent import run_internet_search
        
        # Test with LLM enhancement
        print("🔍 Testing with LLM enhancement...")
        
        result = run_internet_search(
            query="What is machine learning?",
            use_llm=True
        )
        
        if "error" not in result:
            print(f"✅ Success! Found {result.get('total_results', 0)} results")
            
            if result.get('llm_summary'):
                print(f"\n🤖 LLM Summary:")
                print(result['llm_summary'])
            else:
                print("⚠️ No LLM summary generated")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main demonstration function"""
    
    print("🚀 Quiz Detail API Demonstration")
    print("=" * 50)
    
    # Check environment
    print("🔧 Environment Check:")
    print(f"   SERPERDEV_API_KEY: {'✅ Set' if os.getenv('SERPERDEV_API_KEY') else '❌ Not set'}")
    print(f"   GEMINI_API_KEY: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Not set'}")
    print()
    
    # Run demonstrations
    demo_internet_search()
    demo_langgraph_agent()
    
    print("\n" + "=" * 50)
    print("🏁 Demonstration completed!")
    print("\n💡 To test the full API endpoint:")
    print("   1. Start your FastAPI server: uvicorn src.api.main:app --reload")
    print("   2. Run: python test_quiz_detail_api.py")

if __name__ == "__main__":
    main() 