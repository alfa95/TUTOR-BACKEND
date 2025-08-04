from src.agents.readonly_tools import fetch_sessions, filter_sessions_by_score, aggregate_topic_performance
import os
import json
import openai
from bson import ObjectId

def convert_objectid(obj):
    if isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_sessions",
            "description": "Fetch quiz sessions for a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "limit": {"type": "integer", "description": "Number of sessions to fetch"},
                    "sort_by": {"type": "string", "description": "Field to sort by"},
                    "order": {"type": "string", "enum": ["asc", "desc"], "description": "Sort order"}
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_sessions_by_score",
            "description": "Filter sessions by score.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sessions": {"type": "array", "items": {"type": "object"}},
                    "min_score": {"type": "integer"},
                    "max_score": {"type": "integer"}
                },
                "required": ["sessions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "aggregate_topic_performance",
            "description": "Aggregate topic performance from a list of sessions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sessions": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["sessions"]
            }
        }
    }
]

tool_map = {
    "fetch_sessions": fetch_sessions,
    "filter_sessions_by_score": filter_sessions_by_score,
    "aggregate_topic_performance": aggregate_topic_performance,
}

def run_openai_query(prompt, email):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [
        {"role": "system", "content": f"You are a quiz analytics assistant. The user's email is always provided as context: {email}. Use this email for all tool calls."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto"
    )
    message = response.choices[0].message
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        arguments["email"] = email
        result = tool_map[function_name](**arguments)
        messages.append({"role": "assistant", "content": None, "tool_call_id": tool_call.id, "function_call": tool_call.function})
        messages.append({"role": "function", "name": function_name, "content": json.dumps(convert_objectid(result))})
        final_response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=messages
        )
        return final_response.choices[0].message.content
    else:
        return message.content 