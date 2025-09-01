#!/usr/bin/env python3
"""
Debug script to test reranking service and identify issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.reranking_service import reranking_service, SearchResult

def test_reranking_service():
    """Test the reranking service directly"""
    
    print("🔍 Testing Reranking Service Directly")
    print("=" * 50)
    
    # Create test search results
    test_results = [
        SearchResult(
            title="Machine Learning Basics - Introduction to ML",
            link="https://example.com/ml-basics",
            snippet="Learn the fundamentals of machine learning including supervised and unsupervised learning",
            position=1
        ),
        SearchResult(
            title="AI vs Machine Learning - What's the Difference?",
            link="https://example.com/ai-vs-ml",
            snippet="Understanding the relationship between artificial intelligence and machine learning",
            position=2
        ),
        SearchResult(
            title="Python Machine Learning Tutorial",
            link="https://example.com/python-ml",
            snippet="Step-by-step guide to implementing ML algorithms in Python",
            position=3
        ),
        SearchResult(
            title="Machine Learning Applications in Healthcare",
            link="https://example.com/ml-healthcare",
            snippet="How ML is revolutionizing medical diagnosis and treatment",
            position=4
        )
    ]
    
    test_query = "What is machine learning and how does it work?"
    
    print(f"Query: {test_query}")
    print(f"Results to rerank: {len(test_results)}")
    print()
    
    # Test semantic relevance reranking
    print("🧠 Testing Semantic Relevance Reranking")
    print("-" * 40)
    
    try:
        reranked = reranking_service._semantic_relevance_reranking(test_query, test_results)
        
        print("✅ Reranking completed!")
        print("Reranked results:")
        
        for i, result in enumerate(reranked, 1):
            print(f"  {i}. Position {result.position}: {result.title[:50]}...")
            print(f"     Relevance Score: {result.relevance_score}")
            print()
            
    except Exception as e:
        print(f"❌ Semantic reranking failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test query intent reranking
    print("🎯 Testing Query Intent Reranking")
    print("-" * 40)
    
    try:
        reranked = reranking_service._query_intent_reranking(test_query, test_results)
        
        print("✅ Intent reranking completed!")
        print("Reranked results:")
        
        for i, result in enumerate(reranked, 1):
            print(f"  {i}. Position {result.position}: {result.title[:50]}...")
            print(f"     Relevance Score: {result.relevance_score}")
            print()
            
    except Exception as e:
        print(f"❌ Intent reranking failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test full reranking service
    print("🚀 Testing Full Reranking Service")
    print("-" * 40)
    
    try:
        # Convert to dict format for testing
        test_dicts = [
            {
                "title": result.title,
                "link": result.link,
                "snippet": result.snippet,
                "position": result.position
            }
            for result in test_results
        ]
        
        reranked_dicts = reranking_service.rerank_results(
            test_query, 
            test_dicts, 
            strategy="semantic_relevance"
        )
        
        print("✅ Full reranking service completed!")
        print("Final results:")
        
        for i, result in enumerate(reranked_dicts, 1):
            print(f"  {i}. {result['title'][:50]}...")
            print(f"     Original Position: {result['position']}")
            print(f"     Rerank Position: {result['rerank_position']}")
            print(f"     Relevance Score: {result['relevance_score']}")
            print()
            
    except Exception as e:
        print(f"❌ Full reranking service failed: {e}")
        import traceback
        traceback.print_exc()

def test_llm_response_parsing():
    """Test LLM response parsing specifically"""
    
    print("🔍 Testing LLM Response Parsing")
    print("=" * 50)
    
    # Simulate different LLM response formats
    test_responses = [
        # Clean JSON
        '[{"position": 1, "relevance_score": 0.95}, {"position": 2, "relevance_score": 0.87}]',
        
        # JSON with extra text
        'Here are the reranked results:\n[{"position": 1, "relevance_score": 0.95}, {"position": 2, "relevance_score": 0.87}]\nThe results are now ordered by relevance.',
        
        # Malformed JSON
        '[{"position": 1, "relevance_score": 0.95}, {"position": 2, "relevance_score": 0.87}',
        
        # Empty response
        ''
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"Test {i}: {response[:50]}...")
        
        try:
            # Test the parsing logic
            cleaned_response = response.strip()
            
            if "[" in cleaned_response and "]" in cleaned_response:
                start_idx = cleaned_response.find("[")
                end_idx = cleaned_response.rfind("]") + 1
                json_part = cleaned_response[start_idx:end_idx]
                parsed = json.loads(json_part)
                print(f"  ✅ Parsed successfully: {parsed}")
            else:
                parsed = json.loads(cleaned_response)
                print(f"  ✅ Direct parse successful: {parsed}")
                
        except Exception as e:
            print(f"  ❌ Parse failed: {e}")
        
        print()

if __name__ == "__main__":
    print("🚀 Reranking Service Debug Tool")
    print("=" * 60)
    
    # Test LLM response parsing
    test_llm_response_parsing()
    
    print()
    
    # Test reranking service
    test_reranking_service()
    
    print("=" * 60)
    print("🏁 Debug testing completed!") 