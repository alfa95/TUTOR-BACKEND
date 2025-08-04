#!/usr/bin/env python3
"""
Workflow script to build the complete knowledge base system.
This script combines both steps:
1. Combine all Excel files into knowledge_base.xlsx
2. Load the knowledge base into Qdrant vector database
"""

import sys
import os
import subprocess

def run_script(script_name, description):
    """Run a script and handle errors."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Error!")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Failed to run {script_name}: {e}")
        return False
    
    return True

def main():
    """Main workflow function."""
    print("🚀 Starting Knowledge Base Build Workflow")
    print("This will combine all Excel files and index them in Qdrant")
    
    # Step 1: Combine Excel files
    if not run_script("combine_knowledge_base.py", "Step 1: Combining Excel files into knowledge base"):
        print("\n❌ Failed at step 1. Stopping workflow.")
        return
    
    # Step 2: Load into Qdrant
    if not run_script("update_qdrant.py", "Step 2: Loading knowledge base into Qdrant"):
        print("\n❌ Failed at step 2. Stopping workflow.")
        return
    
    print(f"\n{'='*60}")
    print("🎉 Knowledge Base Build Complete!")
    print(f"{'='*60}")
    print("✅ All Excel files combined into knowledge_base.xlsx")
    print("✅ Knowledge base indexed in Qdrant vector database")
    print("\n🎯 You can now use semantic search:")
    print("   from src.vector_store.qdrant_utils import search_similar_questions")
    print("   results = search_similar_questions('your query here')")

if __name__ == "__main__":
    main() 