import os
import logging
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import HuggingFaceHub
import openai

logging.basicConfig(level=logging.INFO)

ModelType = Literal["gemini", "hf"]

def route_llm(model_type: ModelType = "gemini", model_name: str = None):
    logging.info(f"Routing to model type: {model_type}")

    if model_type == "gemini":
        google_api_key = os.getenv("GEMINI_API_KEY")
        if not google_api_key:
            raise EnvironmentError("GEMINI_API_KEY not found in environment variables.")

        return ChatGoogleGenerativeAI(
            model=model_name or "gemini-pro",
            google_api_key=google_api_key,
            temperature=0.2
        )

    elif model_type == "hf":
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not hf_token:
            raise EnvironmentError("HUGGINGFACEHUB_API_TOKEN not found in environment variables.")

        return HuggingFaceHub(
            repo_id=model_name or "mistralai/Mistral-7B-Instruct-v0.1",
            model_kwargs={"temperature": 0.2, "max_new_tokens": 512}
        )

    else:
        raise ValueError(f"Unsupported model type: {model_type}")
