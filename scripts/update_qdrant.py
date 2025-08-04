#!/usr/bin/env python3
"""
Script to update Qdrant vector database from the knowledge base Excel file.
This script uses the existing qdrant_utils to load and index the knowledge base.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vector_store.qdrant_utils import load_excel_and_index, qdrant_client, COLLECTION_NAME

def main():
    """Load the knowledge base into Qdrant."""
    knowledge_base_path = "data/knowledge_base.xlsx"
    
    if not os.path.exists(knowledge_base_path):
        print(f"❌ Knowledge base file not found: {knowledge_base_path}")
        print("Please run combine_knowledge_base.py first to create the knowledge base.")
        return
    
    print("🚀 Loading knowledge base into Qdrant...")
    print(f"📁 Source: {knowledge_base_path}")
    
    try:
        # Load and index the knowledge base
        load_excel_and_index(knowledge_base_path)
        
        # Get collection info
        info = qdrant_client.get_collection(COLLECTION_NAME)
        
        print("\n✅ Successfully updated Qdrant database!")
        print(f"📊 Collection: {COLLECTION_NAME}")
        print(f"🔢 Total vectors: {info.points_count}")
        print(f"📏 Vector size: {info.config.params.vectors.size}")
        print(f"📐 Distance metric: {info.config.params.vectors.distance}")
        
        print("\n🎯 You can now use the search functions:")
        print("   from src.vector_store.qdrant_utils import search_similar_questions")
        print("   results = search_similar_questions('your query here')")
        
    except Exception as e:
        print(f"❌ Error updating Qdrant: {e}")
        return

if __name__ == "__main__":
    main() 