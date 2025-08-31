import hashlib
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import pandas as pd
from collections import defaultdict
from src.llm.embedder import get_embedding
from typing import List, Dict

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if QDRANT_URL:
    # Cloud deployment
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    print(f"🔗 Connected to Qdrant Cloud: {QDRANT_URL}")
else:
    # Local development
    qdrant_client = QdrantClient(path="data/qdrant")
    print("🔗 Connected to local Qdrant")

COLLECTION_NAME = "gktoday_questions"
VECTOR_SIZE = 384

existing_collections = [col.name for col in qdrant_client.get_collections().collections]
if COLLECTION_NAME not in existing_collections:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )

def generate_question_id(row):
    unique_string = f"{row['Date']}_{row['Question']}"
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

def add_questions_to_qdrant(df):
    required_cols = ['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer', 'Date']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    points = []
    added, skipped = 0, 0
    seen_ids = set()

    for idx, row in df.iterrows():
        question_id = generate_question_id(row)

        # Avoid duplicates within the same run
        if question_id in seen_ids:
            skipped += 1
            continue
        seen_ids.add(question_id)

        text_for_embedding = f"{row['Question']} {row.get('Notes', '')} {row.get('Topic', '')} {row.get('Difficulty', '')}"
        embedding = get_embedding(text_for_embedding)

        payload = {
            "uuid": question_id,
            "date": str(row['Date']),
            "question": row['Question'],
            "option_a": row['Option A'],
            "option_b": row['Option B'],
            "option_c": row['Option C'],
            "option_d": row['Option D'],
            "answer": row['Correct Answer'],
            "notes": row.get('Notes', ''),
            "topic": row.get('Topic', 'Unknown'),
            "difficulty": row.get('Difficulty', 'Medium')
        }

        points.append(PointStruct(id=question_id, vector=embedding, payload=payload))
        added += 1

    if points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ {added} new questions added to Qdrant, {skipped} skipped (duplicates in batch).")

def search_similar_questions(query, top_k=5, filters=None):
    query_embedding = get_embedding(query)

    search_filter = None
    if filters:
        conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filters.items()]
        search_filter = Filter(must=conditions)

    response = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,  # Pass list of floats directly
        limit=top_k,
        query_filter=search_filter,
        with_payload=True
    )

    # `response` contains `.points`, which hold payload and score
    hits = response.points if hasattr(response, "points") else response

    results = []
    for point in hits:
        payload = point.payload
        results.append({
            "uuid": payload.get("uuid"),
            "question": payload.get("question"),
            "options": {
                "a": payload.get("option_a"),
                "b": payload.get("option_b"),
                "c": payload.get("option_c"),
                "d": payload.get("option_d"),
            },
            "answer": payload.get("answer"),
            "notes": payload.get("notes", ""),
            "topic": payload.get("topic"),
            "difficulty": payload.get("difficulty"),
            "score": point.score
        })
    return results

def get_all_available_skills_from_vector_db() -> List[Dict]:
    """
    Get all available skills/topics from the vector database with proper labeling
    """
    try:
        # Get all questions to extract unique topics and difficulties
        response = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={},  # No filter to get all
            limit=10000,  # Get more to ensure we cover all topics
            with_payload=True
        )
        
        if not response or not response[0]:
            print("⚠️ No questions found in vector DB")
            return []
        
        # Extract unique topics and difficulties
        topic_data = defaultdict(set)
        topic_counts = defaultdict(int)
        
        for question in response[0]:
            if hasattr(question, 'payload'):
                payload = question.payload
            else:
                payload = question.get('payload', {})
            
            topic = payload.get('topic', 'Unknown')
            difficulty = payload.get('difficulty', 'Medium')
            
            if topic and topic != 'Unknown' and topic != 'Unclassified':
                topic_data[topic].add(difficulty)
                topic_counts[topic] += 1
        
        # Convert to structured format with labels
        skills = []
        for topic, difficulties in topic_data.items():
            # Create labels based on topic content
            labels = _generate_topic_labels(topic)
            
            # Calculate importance score based on question count
            importance_score = min(topic_counts[topic] / 100, 1.0)  # Normalize to 0-1
            
            # Use exact difficulty levels from vector DB
            available_difficulties = list(difficulties)
            
            # Determine overall difficulty level based on available difficulties
            # If topic has multiple difficulties, use the highest one
            if 'Hard' in difficulties:
                difficulty_level = 'Hard'
            elif 'Medium' in difficulties:
                difficulty_level = 'Medium'
            elif 'Easy' in difficulties:
                difficulty_level = 'Easy'
            else:
                difficulty_level = 'Medium'  # Default fallback
            
            skills.append({
                "id": topic.lower().replace(' ', '_').replace('&', 'and').replace('-', '_'),
                "name": topic,  # Use exact topic name from vector DB
                "difficulty": difficulty_level,  # Use exact difficulty from vector DB
                "estimated_time": _estimate_time_for_topic(topic, difficulty_level),
                "importance_score": importance_score,
                "prerequisites": [],  # Will be populated based on topic relationships
                "related_skills": _get_related_topics(topic),
                "career_relevance": _get_career_relevance(topic),
                "labels": labels,
                "available_difficulties": available_difficulties,  # All available difficulties
                "question_count": topic_counts[topic]
            })
        
        # Sort by importance and difficulty
        skills.sort(key=lambda x: (x["importance_score"], x["difficulty"]), reverse=True)
        
        print(f"🎯 Found {len(skills)} available skills from vector DB")
        return skills
        
    except Exception as e:
        print(f"❌ Error fetching available skills from vector DB: {e}")
        return []

def _generate_topic_labels(topic: str) -> List[str]:
    """Generate appropriate labels for a topic based on exact vector DB names"""
    labels = []
    
    # Core subject labels based on exact topic names
    if topic == 'Polity':
        labels.extend(['government', 'constitution', 'politics', 'civics', 'democracy'])
    elif topic == 'Economy':
        labels.extend(['finance', 'business', 'economics', 'commerce', 'trade'])
    elif topic == 'Geography':
        labels.extend(['earth_sciences', 'environment', 'physical_geography', 'human_geography', 'maps'])
    elif topic == 'History':
        labels.extend(['heritage', 'culture', 'ancient', 'modern', 'timeline'])
    elif topic == 'Science & Tech':
        labels.extend(['technology', 'innovation', 'research', 'discovery', 'engineering'])
    elif topic == 'Environment':
        labels.extend(['ecology', 'sustainability', 'climate', 'conservation', 'nature'])
    elif topic == 'Current Affairs':
        labels.extend(['news', 'events', 'trends', 'updates', 'recent'])
    
    # Add general labels
    labels.extend(['competitive_exams', 'general_knowledge', 'interview_prep'])
    
    return list(set(labels))  # Remove duplicates

def _estimate_time_for_topic(topic: str, difficulty: str) -> int:
    """Estimate learning time for a topic in minutes based on exact names"""
    base_time = 45  # Base time in minutes
    
    # Adjust based on exact topic name
    if topic == 'Polity':
        base_time = 60
    elif topic == 'Economy':
        base_time = 75
    elif topic == 'Geography':
        base_time = 50
    elif topic == 'History':
        base_time = 90
    elif topic == 'Science & Tech':
        base_time = 60
    elif topic == 'Environment':
        base_time = 55
    elif topic == 'Current Affairs':
        base_time = 40
    
    # Adjust based on exact difficulty from vector DB
    if difficulty == 'Easy':
        return base_time
    elif difficulty == 'Medium':
        return int(base_time * 1.3)
    else:  # Hard (if exists)
        return int(base_time * 1.8)

def _get_related_topics(topic: str) -> List[str]:
    """Get related topics based on exact subject relationships"""
    related_map = {
        'Polity': ['Current Affairs', 'History', 'Geography'],
        'Economy': ['Current Affairs', 'Geography', 'Science & Tech'],
        'Geography': ['Current Affairs', 'Environment', 'History'],
        'History': ['Current Affairs', 'Geography', 'Polity'],
        'Science & Tech': ['Current Affairs', 'Environment', 'Economy'],
        'Environment': ['Geography', 'Current Affairs', 'Science & Tech'],
        'Current Affairs': ['Polity', 'Economy', 'Geography', 'History', 'Science & Tech', 'Environment']
    }
    
    return related_map.get(topic, ['Current Affairs'])

def _get_career_relevance(topic: str) -> List[str]:
    """Get career relevance for exact topic names"""
    career_map = {
        'Polity': ['civil_services', 'law', 'politics', 'public_administration'],
        'Economy': ['finance', 'business', 'economics', 'banking', 'consulting'],
        'Geography': ['environmental_science', 'tourism', 'urban_planning', 'research'],
        'History': ['education', 'research', 'tourism', 'cultural_heritage'],
        'Science & Tech': ['engineering', 'research', 'technology', 'innovation'],
        'Environment': ['environmental_science', 'conservation', 'policy', 'research'],
        'Current Affairs': ['journalism', 'civil_services', 'politics', 'business']
    }
    
    return career_map.get(topic, ['general_knowledge', 'competitive_exams'])

# ✅ Helper to load Excel and embed to Qdrant
def load_excel_and_index(filepath):
    df = pd.read_excel(filepath)
    add_questions_to_qdrant(df)

# Example usage
if __name__ == "__main__":
    load_excel_and_index("data/processed/gktoday_june.xlsx")
    results = search_similar_questions("India's satellite launch", filters={"topic": "Science & Tech"})
    for r in results:
        print(r)
