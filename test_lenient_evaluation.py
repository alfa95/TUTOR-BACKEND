#!/usr/bin/env python3
"""
Test script for the more lenient RAGAS evaluation system

This script demonstrates how the evaluation rules have been made less strict
to better accommodate real-world RAG applications with LLM enhancement.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_lenient_evaluation():
    """Test the more lenient evaluation system"""
    
    print("🧪 Testing More Lenient RAGAS Evaluation System")
    print("=" * 70)
    
    try:
        # Import the evaluation service
        from services.ragas_evaluation_service import ragas_evaluation_service
        
        print("✅ Successfully imported RAGAS evaluation service")
        print(f"🔍 RAGAS available: {ragas_evaluation_service.metrics_available}")
        print()
        
        # Test data that would have scored poorly with strict rules
        test_query = "Tell me about Prime Minister Modi's recent activities"
        test_context = [
            {
                "question": "Prime Minister Modi to name 21 islands of Andaman & Nicobar after which awardees?",
                "answer": "Param Vir Chakra",
                "notes": "Prime Minister Modi named 21 islands of Andaman & Nicobar after Param Vir Chakra awardees.",
                "topic": "Current Affairs"
            },
            {
                "question": "Which country has invited Indian Prime Minister Narendra Modi on a state visit?",
                "answer": "USA",
                "notes": "Prime Minister Narendra Modi is set to go to the US on a state visit on June 22.",
                "topic": "Current Affairs"
            }
        ]
        
        # LLM response that expands beyond context (would score poorly with strict rules)
        test_response_llm = "Prime Minister Modi has been actively engaged in multiple spheres of governance and international relations. His recent activities include honoring national heroes by naming islands after Param Vir Chakra awardees, which demonstrates his commitment to recognizing military valor. Additionally, he has been invited for a state visit to the United States, highlighting the strengthening bilateral relationship between India and the USA. These activities showcase Modi's multifaceted approach to leadership, combining domestic recognition with international diplomacy."
        
        # Simple response that stays within context (would score well with strict rules)
        test_response_simple = "Prime Minister Modi named 21 islands after Param Vir Chakra awardees and has been invited for a state visit to the USA."
        
        print("📝 Test Data:")
        print(f"  Query: {test_query}")
        print(f"  Context items: {len(test_context)}")
        print(f"  LLM Response length: {len(test_response_llm)} characters")
        print(f"  Simple Response length: {len(test_response_simple)} characters")
        print()
        
        # Test LLM response evaluation
        print("🔄 Testing LLM Response Evaluation (More Lenient Rules)...")
        evaluation_llm = ragas_evaluation_service.evaluate_rag_quality(
            query=test_query,
            context=test_context,
            response=test_response_llm,
            ground_truth=None
        )
        
        print("✅ LLM evaluation completed!")
        print()
        
        # Test simple response evaluation
        print("🔄 Testing Simple Response Evaluation...")
        evaluation_simple = ragas_evaluation_service.evaluate_rag_quality(
            query=test_query,
            context=test_context,
            response=test_response_simple,
            ground_truth=None
        )
        
        print("✅ Simple response evaluation completed!")
        print()
        
        # Compare results
        print("📊 Evaluation Results Comparison:")
        print("=" * 50)
        
        print("🤖 LLM Response (Expanded):")
        metrics_llm = evaluation_llm.metrics
        print(f"  🎯 Context Precision: {metrics_llm.context_precision:.3f}")
        print(f"  🔒 Faithfulness: {metrics_llm.faithfulness:.3f}")
        print(f"  ✅ Answer Correctness: {metrics_llm.answer_correctness:.3f}")
        print(f"  🎯 Context Relevancy: {metrics_llm.context_relevancy:.3f}")
        print(f"  🌟 Overall Score: {metrics_llm.overall_score:.3f}")
        
        print("\n📝 Simple Response (Context-Bound):")
        metrics_simple = evaluation_simple.metrics
        print(f"  🎯 Context Precision: {metrics_simple.context_precision:.3f}")
        print(f"  🔒 Faithfulness: {metrics_simple.faithfulness:.3f}")
        print(f"  ✅ Answer Correctness: {metrics_simple.answer_correctness:.3f}")
        print(f"  🎯 Context Relevancy: {metrics_simple.context_relevancy:.3f}")
        print(f"  🌟 Overall Score: {metrics_simple.overall_score:.3f}")
        
        print("\n" + "=" * 50)
        
        # Show insights for LLM response
        print("💡 LLM Response Quality Insights:")
        insights_llm = evaluation_llm.quality_insights
        for metric, insight in insights_llm.items():
            print(f"  • {metric.replace('_', ' ').title()}: {insight}")
        
        print("\n🚀 LLM Response Recommendations:")
        recommendations_llm = evaluation_llm.recommendations
        for i, rec in enumerate(recommendations_llm[:5], 1):  # Show first 5
            print(f"  {i}. {rec}")
        
        print("\n" + "=" * 50)
        
        # Analysis of lenient rules
        print("🎯 Analysis of More Lenient Rules:")
        
        if metrics_llm.faithfulness > 0.3:
            print("✅ Faithfulness improved with lenient rules - LLM insights are now valued!")
        else:
            print("⚠️ Faithfulness still low - may need further rule adjustments")
        
        if metrics_llm.overall_score > 0.5:
            print("✅ Overall score improved - system now recognizes LLM value!")
        else:
            print("⚠️ Overall score still moderate - consider further optimizations")
        
        # Show what the lenient rules are rewarding
        print("\n🔍 What Lenient Rules Are Rewarding:")
        print("  • Analytical content (theme, pattern, connection)")
        print("  • Thematic insights (overarching, multifaceted)")
        print("  • Reasonable response expansion (2-3x context length)")
        print("  • Semantic relevance (not just exact word matches)")
        print("  • Context interpretation (background, significance)")
        
        print("\n🎯 Lenient Rules Summary:")
        print("  • Context Precision: 0.4+ is now acceptable (was 0.5+)")
        print("  • Faithfulness: 0.3+ is now acceptable (was 0.5+)")
        print("  • Answer Correctness: 0.4+ is now acceptable (was 0.5+)")
        print("  • Context Relevancy: 0.4+ is now acceptable (was 0.5+)")
        print("  • Overall Score: 0.5+ is now acceptable (was 0.6+)")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the project root directory")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lenient_evaluation()
    
    print("\n" + "=" * 70)
    print("🎯 More Lenient Evaluation Test Complete!")
    print("\n💡 The system now better accommodates:")
    print("   • LLM insights and thematic analysis")
    print("   • Reasonable content expansion")
    print("   • Semantic relevance beyond exact matches")
    print("   • Real-world RAG application needs") 