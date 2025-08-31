# Quiz Detail API Documentation

## Overview

The `quiz-detail` API endpoint provides internet search results for quiz questions using LangGraph orchestration and SerperDev for web search. This endpoint fetches the top 4 most relevant results from the internet for any given query.

## Features

- **Internet Search**: Uses SerperDev API to fetch real-time web search results
- **LangGraph Integration**: Orchestrates the search workflow using LangGraph
- **Optional LLM Enhancement**: Can enhance results with AI-generated summaries
- **Flexible Querying**: Supports additional context and model selection
- **Error Handling**: Comprehensive error handling and validation

## API Endpoint

```
POST /quiz-detail
```

## Request Body

```json
{
  "query": "string (required)",
  "use_llm": "boolean (optional, default: false)"
}
```

### Parameters

- **query** (required): The search query/question
- **use_llm** (optional): Whether to use LLM for result enhancement (default: false)

## Response Format

### Success Response (200)

```json
{
  "query": "What is the capital of France?",
  "results": [
    {
      "title": "Paris - Wikipedia",
      "link": "https://en.wikipedia.org/wiki/Paris",
      "snippet": "Paris is the capital and most populous city of France...",
      "position": 1
    },
    {
      "title": "Paris | History, Map, Population, Facts, & Points of Interest",
      "link": "https://www.britannica.com/place/Paris",
      "snippet": "Paris, city and capital of France, situated in the north-central part of the country...",
      "position": 2
    }
  ],
  "total_results": 4,
  "llm_summary": "Based on the search results, Paris is the capital city of France...",
  "model_used": "gemini:gemini-1.5-flash"
}
```

### Error Response (4xx/5xx)

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Example Usage

### Basic Search

```bash
curl -X POST "http://localhost:8000/quiz-detail" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the largest planet in our solar system?"
  }'
```

### Search with LLM Enhancement

```bash
curl -X POST "http://localhost:8000/quiz-detail" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who invented the telephone?",
    "use_llm": true
  }'
```

## Setup Requirements

### Environment Variables

Add the following to your `.env` file:

```bash
SERPERDEV_API_KEY=your_serperdev_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here  # Required if use_llm=true
```

### Dependencies

The following packages are required:

```bash
pip install langgraph requests fastapi uvicorn google-generativeai
```

## Architecture

### LangGraph Workflow

1. **Process Query Node**: Validates and processes the input query
2. **Search Node**: Performs internet search using SerperDev API
3. **Generate Response Node**: Formats results and optionally enhances with LLM

### Tool Integration

- **SerperDev API**: For web search functionality
- **LangGraph**: For workflow orchestration
- **LLM Models**: For optional result enhancement (Gemini, OpenAI, etc.)

## Error Handling

The API handles various error scenarios:

- **Missing API Keys**: Returns 500 error if SERPERDEV_API_KEY is not configured
- **Invalid Queries**: Returns 400 error for empty or invalid queries
- **Search Failures**: Returns 500 error with details about search failures
- **LLM Failures**: Gracefully handles LLM errors and continues without enhancement

## Rate Limits

- SerperDev API has its own rate limits (check your plan)
- LLM API calls are subject to respective provider limits
- Consider implementing request throttling for production use

## Testing

Use the provided test script to verify functionality:

```bash
python test_quiz_detail_api.py
```

Make sure your server is running on `http://localhost:8000` before testing.

## Production Considerations

1. **API Key Security**: Ensure API keys are properly secured in production
2. **Rate Limiting**: Implement appropriate rate limiting
3. **Caching**: Consider caching frequent search results
4. **Monitoring**: Add logging and monitoring for API usage
5. **Error Tracking**: Implement proper error tracking and alerting

## Troubleshooting

### Common Issues

1. **SERPERDEV_API_KEY not found**: Check your `.env` file and environment variables
2. **Search timeouts**: Increase timeout values for complex queries
3. **LLM enhancement failures**: Verify your LLM API keys and quotas
4. **CORS issues**: Ensure proper CORS configuration for your frontend

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export DEBUG=true
```

## Support

For issues or questions:
1. Check the error logs
2. Verify API key configuration
3. Test with the provided test script
4. Check SerperDev API status and quotas 