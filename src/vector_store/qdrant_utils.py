import hashlib
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import pandas as pd
from collections import defaultdict
from src.llm.embedder import get_embedding

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
