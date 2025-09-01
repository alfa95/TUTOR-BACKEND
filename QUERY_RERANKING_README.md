# 🚀 Enhanced Query Endpoint with Reranking

## 📋 Overview

The `/query` endpoint has been enhanced with **intelligent reranking capabilities** to provide better search results and improved user experience. This enhancement integrates the same powerful reranking logic used in the `quiz-detail` endpoint.

## 🎯 Key Benefits

### **1. Enhanced Search Quality**
- **Better result ordering** based on semantic relevance
- **Improved accuracy** through LLM-powered reranking
- **Context-aware ranking** considering user intent

### **2. Performance Optimization**
- **Faster information retrieval** with better-ranked results
- **Reduced user scrolling** to find relevant content
- **Higher user satisfaction** scores

### **3. Unified Search Experience**
- **Consistent reranking** across all search endpoints
- **Same quality improvements** for both RAG and internet search
- **Centralized reranking logic** for maintainability

### **4. Intelligent Result Ranking**
- **Semantic relevance scoring** (0.0-1.0)
- **Query intent analysis** for better context understanding
- **Hybrid ranking strategies** combining multiple approaches

## 🔧 API Changes

### **Enhanced QueryRequest Model**
```python
class QueryRequest(BaseModel):
    query: str
    use_llm: bool = False
    enable_reranking: bool = False          # NEW: Enable reranking
    reranking_strategy: str = "semantic_relevance"  # NEW: Choose strategy
```

### **New Reranking Parameters**
- **`enable_reranking`**: Boolean to enable/disable reranking
- **`reranking_strategy`**: Choose from available strategies:
  - `"semantic_relevance"` (default)
  - `"query_intent"`
  - `"hybrid"`

## 🏗️ Architecture Changes

### **Enhanced RAG Graph Flow**
```
Query → Embed → Search Qdrant → Rerank Results → Generate Response
                ↑
        NEW: Reranking Node
```

### **Reranking Integration Points**
1. **Vector Search Results**: Reranks Qdrant search results
2. **LLM Enhancement**: Optional LLM explanation with reranked context
3. **Metadata Enrichment**: Adds relevance scores and rerank positions

## 📊 Response Format

### **Enhanced Response Structure**
```json
{
  "response": {
    "questions": [
      {
        "question": "What is machine learning?",
        "answer": "Machine learning is...",
        "source": "knowledge_base",
        "relevance_score": 0.95,        // NEW: Reranking score
        "rerank_position": 1,           // NEW: Reranked position
        "position": 3                   // Original position
      }
    ],
    "model": "gemini",
    "explanation": "Based on the reranked results...",
    "metadata": {
      "reranking_applied": true,
      "strategy_used": "semantic_relevance"
    }
  }
}
```

## 🚀 Usage Examples

### **Basic Query Without Reranking**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "use_llm": true,
    "enable_reranking": false
  }'
```

### **Query With Reranking Enabled**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "use_llm": true,
    "enable_reranking": true,
    "reranking_strategy": "semantic_relevance"
  }'
```

### **Different Reranking Strategies**
```bash
# Semantic Relevance (default)
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "AI concepts", "enable_reranking": true, "reranking_strategy": "semantic_relevance"}'

# Query Intent
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "AI concepts", "enable_reranking": true, "reranking_strategy": "query_intent"}'

# Hybrid
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "AI concepts", "enable_reranking": true, "reranking_strategy": "hybrid"}'
```

## 🧪 Testing

### **Run Test Suite**
```bash
python test_query_reranking.py
```

### **Test Individual Components**
```bash
# Test without reranking
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "Test query", "enable_reranking": false}'

# Test with reranking
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "Test query", "enable_reranking": true}'
```

## 📈 Performance Impact

### **Expected Overhead**
- **Without Reranking**: Baseline performance
- **With Reranking**: +15-25% response time
- **LLM + Reranking**: +30-40% response time

### **Performance Benefits**
- **Better result quality** justifies slight overhead
- **Reduced user search time** compensates for API latency
- **Improved accuracy** leads to fewer follow-up queries

## 🔍 Reranking Strategies Explained

### **1. Semantic Relevance**
- **Focus**: Content similarity to query
- **Best for**: Factual questions, concept explanations
- **Use case**: "What is machine learning?"

### **2. Query Intent**
- **Focus**: User's underlying goal
- **Best for**: How-to questions, tutorials
- **Use case**: "How to implement neural networks?"

### **3. Hybrid**
- **Focus**: Combines semantic + intent
- **Best for**: Complex queries, research questions
- **Use case**: "Compare different AI approaches"

## 🛠️ Implementation Details

### **Reranking Process**
1. **Vector Search**: Get initial results from Qdrant
2. **Format Conversion**: Convert to reranking service format
3. **LLM Reranking**: Apply chosen strategy with LLM
4. **Result Integration**: Merge reranked results with original metadata
5. **Response Generation**: Generate final response with reranked context

### **Error Handling**
- **Graceful Fallback**: If reranking fails, use original results
- **Logging**: Comprehensive error tracking and debugging
- **Performance Monitoring**: Track reranking success rates

## 🔧 Configuration

### **Environment Variables**
```bash
# Reranking service configuration
RERANKING_ENABLED=true
DEFAULT_RERANKING_STRATEGY=semantic_relevance
RERANKING_TIMEOUT=30
```

### **Service Configuration**
```python
# In reranking_service.py
@dataclass
class RerankingConfig:
    model_type: str = "gemini"
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.1
    max_tokens: int = 1000
    reranking_strategy: str = "semantic_relevance"
```

## 📊 Monitoring & Metrics

### **Reranking Metrics**
- **Success Rate**: Percentage of successful reranking operations
- **Performance Impact**: Response time overhead
- **Quality Improvement**: User satisfaction scores
- **Strategy Effectiveness**: Performance by strategy type

### **Integration with Metrics Service**
```python
# Metrics are automatically recorded for all queries
metrics_service.record_api_call(
    endpoint="/query",
    use_llm=request.use_llm,
    enable_reranking=request.enable_reranking,  # NEW
    response_time=response_time,
    success=True
)
```

## 🚀 Future Enhancements

### **Planned Features**
1. **Adaptive Strategy Selection**: Auto-choose best strategy per query
2. **User Preference Learning**: Remember user's preferred strategies
3. **Batch Reranking**: Process multiple queries simultaneously
4. **Custom Reranking Models**: Support for domain-specific models

### **Performance Optimizations**
1. **Caching**: Cache reranking results for similar queries
2. **Async Processing**: Non-blocking reranking operations
3. **Model Optimization**: Faster, lighter reranking models

## 🔗 Related Endpoints

- **`/quiz-detail`**: Internet search with reranking
- **`/debug/reranking`**: Test reranking service directly
- **`/metrics/*`**: Monitor reranking performance

## 📝 Migration Guide

### **For Existing Users**
- **No Breaking Changes**: All existing queries work unchanged
- **Opt-in Enhancement**: Enable reranking by setting `enable_reranking: true`
- **Backward Compatible**: Default behavior remains the same

### **For New Implementations**
- **Enable by Default**: Set `enable_reranking: true` for best results
- **Choose Strategy**: Select appropriate strategy for your use case
- **Monitor Performance**: Track impact on response times and quality

---

## 🎯 Summary

The enhanced `/query` endpoint with reranking provides:

✅ **Better search results** through intelligent reranking  
✅ **Improved user experience** with more relevant content  
✅ **Unified search quality** across all endpoints  
✅ **Flexible strategy selection** for different use cases  
✅ **Performance monitoring** and optimization insights  

This enhancement transforms the query endpoint from a basic RAG system to an **intelligent, context-aware search engine** that delivers significantly better results! 🚀 