from src.agents.readonly_tools import fetch_sessions, filter_sessions_by_score, aggregate_topic_performance
from src.llm.model_router import route_llm

TOOLS = [
    {
        "name": "fetch_sessions",
        "description": "Fetch quiz sessions for a user. Parameters: email (str), limit (int, optional), sort_by (str, optional), order (str, optional)",
        "function": fetch_sessions
    },
    {
        "name": "filter_sessions_by_score",
        "description": "Filter sessions by score. Parameters: sessions (list), min_score (int, optional), max_score (int, optional)",
        "function": filter_sessions_by_score
    },
    {
        "name": "aggregate_topic_performance",
        "description": "Aggregate topic performance from a list of sessions. Parameters: sessions (list)",
        "function": aggregate_topic_performance
    }
]

llm = route_llm(model_type="gemini", model_name="gemini-1.5-flash")

class LangGraphAgent:
    def __init__(self, tools, llm):
        self.tools = {tool["name"]: tool["function"] for tool in tools}
        self.llm = llm
        self.tool_descriptions = tools

    def run_query(self, prompt, context=None):
        tool_list = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in self.tool_descriptions])
        full_prompt = (
            f"You are a quiz analytics assistant. You have access to the following tools:\n{tool_list}\n"
            f"User query: {prompt}\n"
            "Decide which tools to call and in what order. Return the answer in a clear, human-readable format."
        )
        response = self.llm.invoke(full_prompt)
        return getattr(response, "content", str(response))

langgraph_agent = LangGraphAgent(TOOLS, llm)

def run_nl_query(prompt, context=None):
    return langgraph_agent.run_query(prompt, context) 