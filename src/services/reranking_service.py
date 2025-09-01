import json
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from src.llm.model_router import route_llm

@dataclass
class SearchResult:
    """Structured search result for reranking"""
    title: str
    link: str
    snippet: str
    position: int
    relevance_score: Optional[float] = None
    rerank_position: Optional[int] = None

@dataclass
class RerankingConfig:
    """Configuration for reranking behavior"""
    model_type: str = "gemini"
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.1  # Low temperature for consistent reranking
    max_tokens: int = 1000
    reranking_strategy: str = "semantic_relevance"  # semantic_relevance, query_intent, hybrid

class RerankingService:
    """Service for reranking search results using LLM intelligence"""
    
    def __init__(self, config: Optional[RerankingConfig] = None):
        self.config = config or RerankingConfig()
        self.llm = route_llm(self.config.model_type, self.config.model_name)
        
    def rerank_results(self, query: str, results: List[Dict], 
                      strategy: str = "semantic_relevance") -> List[Dict]:
        """
        Rerank search results based on query relevance
        
        Args:
            query: User's search query
            results: List of search results from SerperDev
            strategy: Reranking strategy to use
            
        Returns:
            Reranked list of results with relevance scores
        """
        if not results:
            print("⚠️ No results to rerank")
            return results
            
        try:
            print(f"🔍 Reranking {len(results)} results using {strategy} strategy")
            print(f"🔍 Query: {query}")
            
            # Convert to structured format
            search_results = [SearchResult(**result) for result in results]
            print(f"🔍 Converted {len(search_results)} results to SearchResult objects")
            
            # Apply reranking strategy
            if strategy == "semantic_relevance":
                reranked = self._semantic_relevance_reranking(query, search_results)
            elif strategy == "query_intent":
                reranked = self._query_intent_reranking(query, search_results)
            elif strategy == "hybrid":
                reranked = self._hybrid_reranking(query, search_results)
            else:
                print(f"⚠️ Unknown strategy '{strategy}', using semantic relevance")
                reranked = self._semantic_relevance_reranking(query, search_results)
            
            print(f"🔍 Reranking strategy '{strategy}' completed, got {len(reranked)} results")
            
            # Convert back to dict format
            reranked_dicts = []
            for i, result in enumerate(reranked):
                # Ensure relevance_score is always set
                if result.relevance_score is None:
                    # Fallback: assign score based on position (higher position = higher score)
                    result.relevance_score = max(0.1, 1.0 - (i * 0.1))
                    print(f"⚠️ Fallback score assigned: position {result.position} → score {result.relevance_score}")
                
                result_dict = {
                    "title": result.title,
                    "link": result.link,
                    "snippet": result.snippet,
                    "position": result.position,
                    "relevance_score": result.relevance_score,
                    "rerank_position": i + 1
                }
                reranked_dicts.append(result_dict)
            
            return reranked_dicts
            
        except Exception as e:
            print(f"❌ Reranking failed: {e}")
            # Return original results if reranking fails
            return results
    
    def _semantic_relevance_reranking(self, query: str, 
                                    results: List[SearchResult]) -> List[SearchResult]:
        """Rerank based on semantic relevance to query"""
        
        prompt = f"""
        You are an expert search result reranker. Given a query and search results, 
        reorder them by relevance and assign relevance scores (0.0 to 1.0).
        
        Query: "{query}"
        
        Search Results:
        {self._format_results_for_llm(results)}
        
        Instructions:
        1. Analyze each result's relevance to the query
        2. Assign a relevance score (0.0 to 1.0) to each result
        3. Reorder results from most relevant to least relevant
        4. Consider: title relevance, snippet content, and overall usefulness
        
        Return ONLY a JSON array with this exact format:
        [
            {{"position": 1, "relevance_score": 0.95}},
            {{"position": 3, "relevance_score": 0.87}},
            {{"position": 2, "relevance_score": 0.82}},
            {{"position": 4, "relevance_score": 0.75}}
        ]
        
        Do not include any other text, just the JSON array.
        """
        
        try:
            response = self.llm.invoke(prompt)
            response_text = getattr(response, "content", str(response))
            
            print(f"🔍 LLM Response: {response_text[:200]}...")  # Debug
            
            # Clean and parse LLM response
            cleaned_response = response_text.strip()
            
            # Try to extract JSON if LLM added extra text
            if "[" in cleaned_response and "]" in cleaned_response:
                start_idx = cleaned_response.find("[")
                end_idx = cleaned_response.rfind("]") + 1
                json_part = cleaned_response[start_idx:end_idx]
                reranking_data = json.loads(json_part)
            else:
                reranking_data = json.loads(cleaned_response)
            
            print(f"🔍 Parsed Reranking Data: {reranking_data}")  # Debug
            
            # Apply reranking
            reranked_results = []
            for item in reranking_data:
                original_position = item.get("position")
                relevance_score = item.get("relevance_score")
                
                print(f"🔍 Processing: position={original_position}, score={relevance_score}")  # Debug
                
                # Find the original result
                original_result = next((r for r in results if r.position == original_position), None)
                if original_result:
                    original_result.relevance_score = float(relevance_score) if relevance_score is not None else 0.0
                    reranked_results.append(original_result)
                    print(f"✅ Updated result {original_position} with score {original_result.relevance_score}")
                else:
                    print(f"⚠️ Could not find result with position {original_position}")
            
            # Sort by relevance score (highest first)
            reranked_results.sort(key=lambda x: x.relevance_score or 0.0, reverse=True)
            
            print(f"🔍 Final reranked results: {[(r.position, r.relevance_score) for r in reranked_results]}")
            
            return reranked_results
            
        except Exception as e:
            print(f"❌ Semantic reranking failed: {e}")
            print(f"🔍 Full error details: {str(e)}")
            import traceback
            traceback.print_exc()
            return results
    
    def _query_intent_reranking(self, query: str, 
                               results: List[SearchResult]) -> List[SearchResult]:
        """Rerank based on query intent and user goals"""
        
        # Analyze query intent
        intent = self._analyze_query_intent(query)
        
        prompt = f"""
        You are an expert at understanding user search intent and reranking results accordingly.
        
        Query: "{query}"
        Detected Intent: {intent}
        
        Search Results:
        {self._format_results_for_llm(results)}
        
        Instructions:
        1. Consider the user's intent: {intent}
        2. Rerank results based on what the user is likely looking for
        3. Assign relevance scores (0.0 to 1.0) considering intent
        4. Prioritize results that best match the user's goal
        
        Return ONLY a JSON array with this exact format:
        [
            {{"position": 1, "relevance_score": 0.92}},
            {{"position": 3, "relevance_score": 0.88}},
            {{"position": 2, "relevance_score": 0.85}},
            {{"position": 4, "relevance_score": 0.78}}
        ]
        
        Do not include any other text, just the JSON array.
        """
        
        try:
            response = self.llm.invoke(prompt)
            response_text = getattr(response, "content", str(response))
            
            print(f"🔍 Query Intent LLM Response: {response_text[:200]}...")  # Debug
            
            # Clean and parse LLM response
            cleaned_response = response_text.strip()
            
            # Try to extract JSON if LLM added extra text
            if "[" in cleaned_response and "]" in cleaned_response:
                start_idx = cleaned_response.find("[")
                end_idx = cleaned_response.rfind("]") + 1
                json_part = cleaned_response[start_idx:end_idx]
                reranking_data = json.loads(json_part)
            else:
                reranking_data = json.loads(cleaned_response)
            
            print(f"🔍 Parsed Intent Reranking Data: {reranking_data}")  # Debug
            
            # Apply reranking
            reranked_results = []
            for item in reranking_data:
                original_position = item.get("position")
                relevance_score = item.get("relevance_score")
                
                print(f"🔍 Processing Intent: position={original_position}, score={relevance_score}")  # Debug
                
                original_result = next((r for r in results if r.position == original_position), None)
                if original_result:
                    original_result.relevance_score = float(relevance_score) if relevance_score is not None else 0.0
                    reranked_results.append(original_result)
                    print(f"✅ Updated intent result {original_position} with score {original_result.relevance_score}")
                else:
                    print(f"⚠️ Could not find intent result with position {original_position}")
            
            reranked_results.sort(key=lambda x: x.relevance_score or 0.0, reverse=True)
            return reranked_results
            
        except Exception as e:
            print(f"❌ Query intent reranking failed: {e}")
            print(f"🔍 Full error details: {str(e)}")
            import traceback
            traceback.print_exc()
            return results
    
    def _hybrid_reranking(self, query: str, 
                         results: List[SearchResult]) -> List[SearchResult]:
        """Combine multiple reranking strategies"""
        
        # Get semantic reranking
        semantic_results = self._semantic_relevance_reranking(query, results)
        
        # Get intent-based reranking
        intent_results = self._query_intent_reranking(query, results)
        
        # Combine scores (weighted average)
        combined_results = []
        for i, result in enumerate(results):
            semantic_score = next((r.relevance_score for r in semantic_results if r.position == result.position), 0.0)
            intent_score = next((r.relevance_score for r in intent_results if r.position == result.position), 0.0)
            
            # Weighted combination (70% semantic, 30% intent)
            combined_score = (semantic_score * 0.7) + (intent_score * 0.3)
            
            result.relevance_score = combined_score
            combined_results.append(result)
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x.relevance_score or 0.0, reverse=True)
        return combined_results
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze the intent behind a user query"""
        
        intent_prompt = f"""
        Analyze this search query and determine the user's intent:
        Query: "{query}"
        
        Choose from these intent categories:
        - "factual": Looking for specific facts or definitions
        - "how_to": Wanting instructions or tutorials
        - "comparison": Comparing options or concepts
        - "explanation": Seeking detailed explanations
        - "examples": Looking for examples or use cases
        - "research": Academic or in-depth research
        
        Return ONLY the intent category, nothing else.
        """
        
        try:
            response = self.llm.invoke(intent_prompt)
            intent = getattr(response, "content", str(response)).strip().lower()
            return intent
        except:
            return "factual"  # Default fallback
    
    def _format_results_for_llm(self, results: List[SearchResult]) -> str:
        """Format search results for LLM processing"""
        formatted = ""
        for i, result in enumerate(results, 1):
            formatted += f"{i}. Title: {result.title}\n"
            formatted += f"   Snippet: {result.snippet}\n"
            formatted += f"   Position: {result.position}\n\n"
        return formatted
    
    def get_reranking_metrics(self, original_results: List[Dict], 
                            reranked_results: List[Dict]) -> Dict:
        """Calculate metrics about reranking performance"""
        
        if not original_results or not reranked_results:
            return {"error": "No results to compare"}
        
        # Calculate position changes
        position_changes = []
        for reranked in reranked_results:
            original_pos = reranked.get("position", 0)
            rerank_pos = reranked.get("rerank_position", 0)
            change = original_pos - rerank_pos
            position_changes.append(change)
        
        # Calculate metrics
        avg_position_improvement = sum(position_changes) / len(position_changes)
        results_improved = len([c for c in position_changes if c > 0])
        results_worsened = len([c for c in position_changes if c < 0])
        
        return {
            "total_results": len(reranked_results),
            "average_position_improvement": round(avg_position_improvement, 2),
            "results_improved": results_improved,
            "results_worsened": results_worsened,
            "results_unchanged": len([c for c in position_changes if c == 0]),
            "improvement_rate": round((results_improved / len(reranked_results)) * 100, 1)
        }

# Global instance
reranking_service = RerankingService() 