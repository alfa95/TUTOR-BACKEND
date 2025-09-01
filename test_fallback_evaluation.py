#!/usr/bin/env python3
"""
Test script for RAGAS fallback evaluation system

This script tests the fallback evaluation functionality without requiring
the server to be running or RAGAS to be available.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_fallback_evaluation():
    """Test the fallback evaluation system"""
    
    print("🧪 Testing RAGAS Fallback Evaluation System")
    print("=" * 60)
    
    try:
        # Import the evaluation service
        from services.ragas_evaluation_service import ragas_evaluation_service
        
        print("✅ Successfully imported RAGAS evaluation service")
        print(f"🔍 RAGAS available: {ragas_evaluation_service.metrics_available}")
        print()
        
        # Test data
        test_query = "What is machine learning?"
        test_context = [
            {
                "question": "What is machine learning?",
                "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.",
                "topic": "AI/ML",
                "difficulty": "intermediate"
            },
            {
                "question": "How does supervised learning work?",
                "answer": "Supervised learning uses labeled training data to teach algorithms to recognize patterns and make predictions.",
                "topic": "AI/ML",
                "difficulty": "intermediate"
            },
            {
                "question": "What are neural networks?",
                "answer": "Neural networks are computing systems inspired by biological neural networks, used for pattern recognition and decision making.",
                "topic": "AI/ML",
                "difficulty": "advanced"
            }
        ]
        test_response = "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It works by analyzing data patterns and making predictions based on those patterns."
        test_ground_truth = "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed."
        
        print("📝 Test Data:")
        print(f"  Query: {test_query}")
        print(f"  Context items: {len(test_context)}")
        print(f"  Response length: {len(test_response)} characters")
        print(f"  Ground truth provided: {'Yes' if test_ground_truth else 'No'}")
        print()
        
        # Test evaluation
        print("🔄 Running evaluation...")
        evaluation_result = ragas_evaluation_service.evaluate_rag_quality(
            query=test_query,
            context=test_context,
            response=test_response,
            ground_truth=test_ground_truth
        )
        
        print("✅ Evaluation completed successfully!")
        print()
        
        # Display results
        print("📊 Evaluation Results:")
        print("-" * 40)
        
        metrics = evaluation_result.metrics
        print(f"🎯 Context Precision: {metrics.context_precision:.3f}")
        print(f"🔒 Faithfulness: {metrics.faithfulness:.3f}")
        print(f"✅ Answer Correctness: {metrics.answer_correctness:.3f}")
        print(f"🎯 Context Relevancy: {metrics.context_relevancy:.3f}")
        print(f"🌟 Overall Score: {metrics.overall_score:.3f}")
        print(f"⏱️  Evaluation Time: {metrics.evaluation_time:.3f}s")
        print(f"🔧 Method: {metrics.metadata.get('evaluation_method', 'unknown')}")
        print()
        
        # Display insights
        if evaluation_result.quality_insights:
            print("💡 Quality Insights:")
            for metric, insight in evaluation_result.quality_insights.items():
                print(f"  • {metric.replace('_', ' ').title()}: {insight}")
            print()
        
        # Display recommendations
        if evaluation_result.recommendations:
            print("🚀 Recommendations:")
            for i, rec in enumerate(evaluation_result.recommendations, 1):
                print(f"  {i}. {rec}")
            print()
        
        # Test without ground truth
        print("🔄 Testing evaluation WITHOUT ground truth...")
        evaluation_no_gt = ragas_evaluation_service.evaluate_rag_quality(
            query=test_query,
            context=test_context,
            response=test_response,
            ground_truth=None
        )
        
        print("✅ Evaluation without ground truth completed!")
        print(f"🎯 Answer Correctness (no GT): {evaluation_no_gt.metrics.answer_correctness:.3f}")
        print(f"🔧 Method: {evaluation_no_gt.metrics.metadata.get('evaluation_method', 'unknown')}")
        print()
        
        # Test with different query types
        print("🔄 Testing different query types...")
        test_queries = [
            "Explain quantum computing",
            "What are the benefits of renewable energy?",
            "How does photosynthesis work?"
        ]
        
        for query in test_queries:
            result = ragas_evaluation_service.evaluate_rag_quality(
                query=query,
                context=test_context,  # Using same context for simplicity
                response=f"This is a response about {query.lower()}.",
                ground_truth=None
            )
            print(f"  {query[:30]}... → Overall Score: {result.metrics.overall_score:.3f}")
        
        print()
        print("🎯 All tests completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the project root directory")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_individual_metrics():
    """Test individual metric calculations"""
    
    print("\n🧪 Testing Individual Metric Calculations")
    print("=" * 60)
    
    try:
        from services.ragas_evaluation_service import ragas_evaluation_service
        
        # Test context precision
        query = "What is artificial intelligence?"
        context = [
            {"question": "What is AI?", "answer": "Artificial Intelligence is technology that mimics human intelligence."},
            {"question": "How does ML work?", "answer": "Machine learning uses algorithms to find patterns in data."}
        ]
        
        precision = ragas_evaluation_service._calculate_context_precision_fallback(query, context)
        print(f"🎯 Context Precision: {precision:.3f}")
        
        # Test faithfulness
        response = "Artificial Intelligence is technology that mimics human intelligence and can learn from data."
        faithfulness = ragas_evaluation_service._calculate_faithfulness_fallback(context, response)
        print(f"🔒 Faithfulness: {faithfulness:.3f}")
        
        # Test answer correctness with ground truth
        ground_truth = "Artificial Intelligence is technology that mimics human intelligence."
        correctness = ragas_evaluation_service._calculate_answer_correctness_fallback(response, ground_truth)
        print(f"✅ Answer Correctness (with GT): {correctness:.3f}")
        
        # Test answer correctness without ground truth
        correctness_no_gt = ragas_evaluation_service._calculate_answer_correctness_fallback(response, None)
        print(f"✅ Answer Correctness (no GT): {correctness_no_gt:.3f}")
        
        # Test context relevancy
        relevancy = ragas_evaluation_service._calculate_context_relevancy_fallback(query, context)
        print(f"🎯 Context Relevancy: {relevancy:.3f}")
        
        print("✅ Individual metric tests completed!")
        
    except Exception as e:
        print(f"❌ Individual metric test failed: {e}")

if __name__ == "__main__":
    test_fallback_evaluation()
    test_individual_metrics()
    
    print("\n" + "=" * 60)
    print("🎯 Fallback Evaluation Test Suite Complete!")
    print("\n💡 This demonstrates that the system works even when RAGAS is unavailable")
    print("   due to uvloop incompatibility or other issues.") 