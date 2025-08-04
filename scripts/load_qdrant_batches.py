#!/usr/bin/env python3
"""
Script to load data into Qdrant in batches to avoid timeouts.
"""

import sys
import os
import pandas as pd
from tqdm import tqdm

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vector_store.qdrant_utils import qdrant_client, COLLECTION_NAME, generate_question_id, PointStruct
from src.llm.embedder import get_embedding

def load_data_in_batches(file_path, batch_size=50):
    """Load data into Qdrant in batches."""
    
    print(f"📖 Reading data from: {file_path}")
    df = pd.read_excel(file_path)
    print(f"📊 Total records: {len(df)}")
    
    # Process in batches
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, len(df))
        
        print(f"\n🔄 Processing batch {batch_num + 1}/{total_batches} (records {start_idx + 1}-{end_idx})")
        
        batch_df = df.iloc[start_idx:end_idx]
        points = []
        
        for idx, row in tqdm(batch_df.iterrows(), total=len(batch_df), desc="Creating embeddings"):
            try:
                question_id = generate_question_id(row)
                
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
                
            except Exception as e:
                print(f"⚠️ Error processing row {idx}: {e}")
                continue
        
        if points:
            try:
                print(f"📤 Uploading {len(points)} points to Qdrant...")
                qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
                print(f"✅ Batch {batch_num + 1} uploaded successfully!")
            except Exception as e:
                print(f"❌ Error uploading batch {batch_num + 1}: {e}")
                return False
    
    return True

def main():
    """Main function."""
    file_path = "knowledge_base.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print("🚀 Starting batch upload to Qdrant Cloud...")
    
    try:
        success = load_data_in_batches(file_path, batch_size=25)  # Smaller batches
        
        if success:
            # Get collection info
            info = qdrant_client.get_collection(COLLECTION_NAME)
            print(f"\n🎉 Successfully loaded data into Qdrant Cloud!")
            print(f"📊 Collection: {COLLECTION_NAME}")
            print(f"🔢 Total vectors: {info.points_count}")
            print(f"📏 Vector size: {info.config.params.vectors.size}")
        else:
            print("❌ Failed to load all data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 