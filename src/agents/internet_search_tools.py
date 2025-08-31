import os
import requests
import json
from typing import List, Dict, Optional

def search_internet(query: str, num_results: int = 4) -> List[Dict]:
    """
    Search the internet using SerperDev API and return top results
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return (default: 4)
    
    Returns:
        List[Dict]: List of search results with title, link, and snippet
    """
    try:
        api_key = os.getenv("SERPERDEV_API_KEY")
        if not api_key:
            raise ValueError("SERPERDEV_API_KEY not found in environment variables")
        
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": num_results
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract organic results
        organic_results = data.get("organic", [])
        
        # Format results
        formatted_results = []
        for result in organic_results[:num_results]:
            formatted_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "position": result.get("position", 0)
            })
        
        return formatted_results
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error in internet search: {e}")
        return [{"error": f"Search request failed: {str(e)}"}]
    except Exception as e:
        print(f"❌ Error in internet search: {e}")
        return [{"error": f"Search failed: {str(e)}"}]

def search_with_context(query: str, context: str = "", num_results: int = 4) -> List[Dict]:
    """
    Search the internet with additional context
    
    Args:
        query (str): The search query
        context (str): Additional context to refine the search
        num_results (int): Number of results to return
    
    Returns:
        List[Dict]: List of search results
    """
    if context:
        enhanced_query = f"{query} {context}".strip()
    else:
        enhanced_query = query
    
    return search_internet(enhanced_query, num_results) 