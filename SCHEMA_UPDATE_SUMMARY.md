# Adaptive Quiz API Schema Update Summary

## Overview
The `/quiz/adaptive-questions` API endpoint has been updated to provide more flexible topic and difficulty selection with a clean, simplified schema.

## Changes Made

### 1. Updated Models (`src/models/quiz_models.py`)
- **Added new `TopicRequest` model:**
  ```python
  class TopicRequest(BaseModel):
      topic: str
      difficulty: Optional[str] = None  # Optional: "Easy", "Medium", "Hard"
  ```

- **Simplified `AdaptiveQuizRequest` model:**
  ```python
  class AdaptiveQuizRequest(BaseModel):
      jwt_token: str
      num_questions: int = 10
      topic_requests: Optional[List[TopicRequest]] = None  # Optional: specific topics and difficulties to focus on
  ```

### 2. Enhanced Service (`src/services/adaptive_quiz_service.py`)
- **Simplified method signature** to only accept `topic_requests`
- **Cleaner filter building logic** for topic-specific requests
- **Intelligent fallback** to system's adaptive logic when no preferences specified
- **Added new methods:**
  - `_build_topic_specific_filter()` - Handles topic_requests structure
  - `_build_default_filter()` - Fallback when no preferences specified

### 3. Updated API Endpoint (`src/api/main.py`)
- **Simplified endpoint** to only pass `topic_requests` parameter
- **Cleaner implementation** without backward compatibility complexity

## New Schema Usage Examples

### Example 1: Topic with Specific Difficulty
```json
{
  "jwt_token": "your_jwt_token",
  "num_questions": 10,
  "topic_requests": [
    {
      "topic": "Current Affairs",
      "difficulty": "Easy"
    },
    {
      "topic": "History",
      "difficulty": "Medium"
    }
  ]
}
```

### Example 2: Topic Only (System Chooses Difficulty)
```json
{
  "jwt_token": "your_jwt_token",
  "num_questions": 15,
  "topic_requests": [
    {
      "topic": "Geography"
    },
    {
      "topic": "Science"
    }
  ]
}
```

### Example 3: No Topic Preferences (System Adaptive)
```json
{
  "jwt_token": "your_jwt_token",
  "num_questions": 8
}
```

## Benefits

1. **Cleaner Schema**: Single field for topic selection eliminates confusion
2. **More Flexible**: Users can specify both topic and difficulty preferences
3. **Better Control**: Topic-specific quizzes with difficulty targeting
4. **Intelligent Fallbacks**: System chooses appropriate topics and difficulties when not specified
5. **Enhanced User Experience**: More personalized quiz generation
6. **Simplified Implementation**: Easier to maintain and understand

## Implementation Details

- **Single Source of Truth**: `topic_requests` is the only way to specify topic preferences
- **Optional Field**: When not provided, system uses intelligent adaptive logic
- **Filter Building**: Creates specific vector database queries based on user preferences
- **Difficulty Handling**: Supports "Easy", "Medium", "Hard" difficulty levels
- **Error Handling**: Graceful fallbacks when invalid requests are provided

## Testing

The schema has been tested with:
- ✅ New topic_requests structure
- ✅ Optional topic_requests (system adaptive mode)
- ✅ Topic with difficulty specification
- ✅ Topic without difficulty (system chooses)
- ✅ Pydantic model validation

## Migration Guide

### For Existing Users
- **Update Required**: Replace `topics` array with `topic_requests` structure
- **Simple Migration**: Convert `["topic1", "topic2"]` to `[{"topic": "topic1"}, {"topic": "topic2"}]`

### For New Implementations
- **Recommended**: Use `topic_requests` structure for better flexibility
- **Best Practice**: Specify difficulty when you want targeted questions
- **Fallback**: Omit difficulty to let system choose based on user progress
- **Optional**: Omit entire field to let system choose topics and difficulties

## Files Modified
1. `src/models/quiz_models.py` - Simplified models
2. `src/services/adaptive_quiz_service.py` - Cleaner service logic
3. `src/api/main.py` - Simplified endpoint

## Next Steps
1. **Deploy changes** to development environment
2. **Update frontend** to use new schema
3. **Test with real data** to ensure filter logic works correctly
4. **Monitor performance** of new filter queries
5. **Gather user feedback** on new flexibility features 