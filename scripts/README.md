# Scripts Directory

This directory contains utility scripts for the tutor backend project.

## 📋 Summary

This directory contains scripts to build a complete knowledge base system:

1. **`combine_knowledge_base.py`** - Combines all Excel files into one knowledge base
2. **`update_qdrant.py`** - Loads the knowledge base into Qdrant vector database  
3. **`build_knowledge_base.py`** - Complete workflow (combines both steps above)

### 🎯 What You Get
- **Combined Excel**: 3,222 unique questions from 21 files
- **Vector Database**: Semantic search with topic filtering
- **Ready-to-Use**: Complete search functionality

## 🚀 Quick Start - Execution Commands

### Prerequisites
```bash
# Activate the virtual environment
source scraper_env/bin/activate
```

### Complete Workflow (Recommended)
```bash
# Run the complete knowledge base build process
python scripts/build_knowledge_base.py
```

### Individual Scripts

#### 1. Combine Excel Files
```bash
# Basic usage (creates knowledge_base.xlsx in current directory)
python scripts/combine_knowledge_base.py

# Custom output location
python scripts/combine_knowledge_base.py --output data/knowledge_base.xlsx

# Custom data directory
python scripts/combine_knowledge_base.py --data-dir data/processed --output my_kb.xlsx

# Verbose logging
python scripts/combine_knowledge_base.py --verbose
```

#### 2. Load into Qdrant Vector Database
```bash
# Load knowledge base into Qdrant
python scripts/update_qdrant.py
```

#### 3. Test Search Functionality
```bash
# Test basic search
python -c "from src.vector_store.qdrant_utils import search_similar_questions; results = search_similar_questions('India economy', top_k=3); [print(f'Q: {r[\"question\"]}\\nA: {r[\"answer\"]}\\nScore: {r[\"score\"]:.3f}\\n') for r in results]"

# Test search with topic filter
python -c "from src.vector_store.qdrant_utils import search_similar_questions; results = search_similar_questions('satellite', filters={'topic': 'Science & Tech'}, top_k=2); [print(f'Q: {r[\"question\"]}\\nA: {r[\"answer\"]}\\nTopic: {r[\"topic\"]}\\nScore: {r[\"score\"]:.3f}\\n') for r in results]"

# Test environment topic search
python -c "from src.vector_store.qdrant_utils import search_similar_questions; results = search_similar_questions('climate change', filters={'topic': 'Environment'}, top_k=2); [print(f'Q: {r[\"question\"]}\\nA: {r[\"answer\"]}\\nScore: {r[\"score\"]:.3f}\\n') for r in results]"
```

#### 4. Check Qdrant Collection Status
```bash
# View collection information
python -c "from src.vector_store.qdrant_utils import qdrant_client, COLLECTION_NAME; info = qdrant_client.get_collection(COLLECTION_NAME); print(f'Collection: {COLLECTION_NAME}'); print(f'Total vectors: {info.points_count}'); print(f'Vector size: {info.config.params.vectors.size}'); print(f'Distance: {info.config.params.vectors.distance}')"
```

### Development Commands

#### Check File Sizes
```bash
# Check knowledge base file size
ls -lh data/knowledge_base.xlsx

# Check Qdrant database size
du -sh data/qdrant/
```

#### Verify Data Integrity
```bash
# Check Excel file structure
python -c "import pandas as pd; df = pd.read_excel('data/knowledge_base.xlsx'); print('Columns:', list(df.columns)); print('Total rows:', len(df)); print('Date range:', df['Date'].min(), 'to', df['Date'].max())"
```

#### Reset and Rebuild
```bash
# Remove existing knowledge base
rm data/knowledge_base.xlsx

# Remove Qdrant database (if needed)
rm -rf data/qdrant/

# Rebuild everything
python scripts/build_knowledge_base.py
```

### Expected Output Examples

#### Successful Build Output
```
🚀 Starting Knowledge Base Build Workflow
This will combine all Excel files and index them in Qdrant

============================================================
🔄 Step 1: Combining Excel files into knowledge base
============================================================
✅ Success!

==================================================
📊 KNOWLEDGE BASE SUMMARY
==================================================
Total Questions: 3222

Topics Distribution:
  Current Affairs: 1709 (53.0%)
  Unclassified: 383 (11.9%)
  Science & Tech: 369 (11.5%)
  Geography: 257 (8.0%)
  Polity: 213 (6.6%)
  Economy: 199 (6.2%)
  Environment: 79 (2.5%)
  Miscellaneous: 13 (0.4%)

Difficulty Distribution:
  Medium: 1967 (61.0%)
  Easy: 1243 (38.6%)
  Hard: 12 (0.4%)

Date Range:
  From: 2023-01-01
  To: 2025-07-29
==================================================

============================================================
🔄 Step 2: Loading knowledge base into Qdrant
============================================================
✅ Success!
🚀 Loading knowledge base into Qdrant...
📁 Source: data/knowledge_base.xlsx
✅ 3222 new questions added to Qdrant, 0 skipped (duplicates in batch).

✅ Successfully updated Qdrant database!
📊 Collection: gktoday_questions
🔢 Total vectors: 3237
📏 Vector size: 384
📐 Distance metric: Cosine

============================================================
🎉 Knowledge Base Build Complete!
============================================================
✅ All Excel files combined into knowledge_base.xlsx
✅ Knowledge base indexed in Qdrant vector database
```

#### Successful Search Output
```
Q: Which organization recently released "India Development Update: India's Trade Opportunities in a Changing Global Context" report?
A: World Bank
Score: 0.670

Q: As per the World Bank's Global Economic Prospects Report, what is the expected economic growth of India in 2023-24?
A: 6.6 %
Score: 0.668
```

### Troubleshooting Commands

#### Check Virtual Environment
```bash
# Verify virtual environment is active
which python
pip list | grep -E "(pandas|openpyxl|qdrant|sentence-transformers)"
```

#### Test Individual Components
```bash
# Test Excel reading
python -c "import pandas as pd; df = pd.read_excel('data/processed/gktoday_2023_1.xlsx'); print('Successfully read:', len(df), 'rows')"

# Test Qdrant connection
python -c "from src.vector_store.qdrant_utils import qdrant_client; print('Qdrant client connected successfully')"

# Test embedding generation
python -c "from src.llm.embedder import get_embedding; embedding = get_embedding('test question'); print('Embedding generated:', len(embedding), 'dimensions')"
```

## combine_knowledge_base.py

A script to combine all Excel files in the `data/processed/` directory into one comprehensive knowledge base.

### Features

- **Automatic Discovery**: Finds all `.xlsx` files in the specified directory
- **Data Combination**: Merges all Excel files into a single DataFrame
- **Deduplication**: Removes duplicate questions based on content (case-insensitive)
- **Data Cleaning**: Removes empty rows and sorts by date and topic
- **Date Formatting**: Converts string dates to proper datetime format
- **Auto-formatting**: Automatically adjusts Excel column widths for better readability
- **Comprehensive Reporting**: Provides detailed statistics about the combined dataset

### Usage

#### Basic Usage
```bash
python scripts/combine_knowledge_base.py
```
This will:
- Search for Excel files in `data/processed/`
- Combine them into `knowledge_base.xlsx` in the current directory

#### Custom Output Location
```bash
python scripts/combine_knowledge_base.py --output data/knowledge_base.xlsx
```

#### Custom Data Directory
```bash
python scripts/combine_knowledge_base.py --data-dir path/to/excel/files --output my_knowledge_base.xlsx
```

#### Verbose Logging
```bash
python scripts/combine_knowledge_base.py --verbose
```

### Command Line Options

- `--data-dir`: Directory containing Excel files (default: `data/processed`)
- `--output`: Output file path (default: `knowledge_base.xlsx`)
- `--verbose, -v`: Enable verbose logging
- `--help, -h`: Show help message

### Output

The script creates an Excel file with the following columns:
- **Date**: Question date (properly formatted as datetime)
- **Question**: The quiz question text
- **Option A, B, C, D**: Multiple choice options
- **Correct Answer**: The correct answer
- **Notes**: Additional explanation or notes
- **Topic**: Question topic (Polity, Economy, Geography, etc.)
- **Difficulty**: Question difficulty (Easy, Medium, Hard)

### Example Output

```
==================================================
📊 KNOWLEDGE BASE SUMMARY
==================================================
Total Questions: 3222

Topics Distribution:
  Current Affairs: 1709 (53.0%)
  Unclassified: 383 (11.9%)
  Science & Tech: 369 (11.5%)
  Geography: 257 (8.0%)
  Polity: 213 (6.6%)
  Economy: 199 (6.2%)
  Environment: 79 (2.5%)
  Miscellaneous: 13 (0.4%)

Difficulty Distribution:
  Medium: 1967 (61.0%)
  Easy: 1243 (38.6%)
  Hard: 12 (0.4%)

Date Range:
  From: 2023-01-01
  To: 2025-07-29

Source Files: 21
==================================================
```

### Requirements

- Python 3.7+
- pandas
- openpyxl

These dependencies are already included in the project's `requirements.txt`.

### Error Handling

The script includes robust error handling:
- Continues processing even if individual files fail to load
- Provides detailed error messages for troubleshooting
- Gracefully handles missing directories or files
- Validates data integrity during processing

### Performance

- Processes files sequentially to manage memory usage
- Uses efficient pandas operations for data manipulation
- Includes progress logging for large datasets
- Optimized for datasets with thousands of questions

## update_qdrant.py

A script to load the knowledge base Excel file into the Qdrant vector database for semantic search.

### Features

- **Automatic Loading**: Loads the combined knowledge base into Qdrant
- **Vector Embedding**: Converts questions to embeddings using sentence transformers
- **Duplicate Prevention**: Prevents duplicate questions using MD5 hashing
- **Status Reporting**: Shows collection statistics after loading

### Usage

#### Basic Usage
```bash
# Activate virtual environment first
source scraper_env/bin/activate

# Update Qdrant from knowledge base
python scripts/update_qdrant.py
```

### Requirements

- Virtual environment with all dependencies installed
- Knowledge base Excel file (`data/knowledge_base.xlsx`)
- Qdrant client and sentence transformers

### Output

The script will:
1. Load the knowledge base Excel file
2. Convert questions to vector embeddings
3. Store them in the Qdrant collection `gktoday_questions`
4. Display collection statistics

### Example Output

```
🚀 Loading knowledge base into Qdrant...
📁 Source: data/knowledge_base.xlsx
✅ 3222 new questions added to Qdrant, 0 skipped (duplicates in batch).

✅ Successfully updated Qdrant database!
📊 Collection: gktoday_questions
🔢 Total vectors: 3237
📏 Vector size: 384
📐 Distance metric: Cosine
```

### Integration

After running this script, you can use the search functions:

```python
from src.vector_store.qdrant_utils import search_similar_questions

# Basic search
results = search_similar_questions("India economy", top_k=5)

# Search with filters
results = search_similar_questions("satellite", filters={"topic": "Science & Tech"})
```

## build_knowledge_base.py

A complete workflow script that automates the entire knowledge base building process.

### Features

- **One-Command Workflow**: Combines both Excel merging and Qdrant indexing
- **Error Handling**: Stops workflow if any step fails
- **Progress Reporting**: Shows detailed progress for each step
- **Complete Setup**: Ready-to-use knowledge base system

### Usage

#### Complete Workflow
```bash
# Activate virtual environment first
source scraper_env/bin/activate

# Run complete workflow
python scripts/build_knowledge_base.py
```

This single command will:
1. Combine all Excel files in `data/processed/` into `knowledge_base.xlsx`
2. Load the knowledge base into Qdrant vector database
3. Provide search functionality

### Workflow Steps

1. **Excel Combination**: Uses `combine_knowledge_base.py`
2. **Qdrant Indexing**: Uses `update_qdrant.py`
3. **Verification**: Confirms successful completion

### Example Output

```
🚀 Starting Knowledge Base Build Workflow
This will combine all Excel files and index them in Qdrant

============================================================
🔄 Step 1: Combining Excel files into knowledge base
============================================================
✅ Success!
[Excel combination output...]

============================================================
🔄 Step 2: Loading knowledge base into Qdrant
============================================================
✅ Success!
[Qdrant indexing output...]

============================================================
🎉 Knowledge Base Build Complete!
============================================================
✅ All Excel files combined into knowledge_base.xlsx
✅ Knowledge base indexed in Qdrant vector database

🎯 You can now use semantic search:
   from src.vector_store.qdrant_utils import search_similar_questions
   results = search_similar_questions('your query here')
```

### When to Use

- **Initial Setup**: First time building the knowledge base
- **Complete Refresh**: When you want to rebuild everything from scratch
- **Automation**: For CI/CD pipelines or scheduled updates

## 🎯 Common Use Cases

### For New Users
```bash
# 1. Activate environment
source scraper_env/bin/activate

# 2. Build complete knowledge base
python scripts/build_knowledge_base.py

# 3. Test search functionality
python -c "from src.vector_store.qdrant_utils import search_similar_questions; results = search_similar_questions('India economy', top_k=3); [print(f'Q: {r[\"question\"]}\\nA: {r[\"answer\"]}\\nScore: {r[\"score\"]:.3f}\\n') for r in results]"
```

### For Developers
```bash
# Check system status
ls -lh data/knowledge_base.xlsx
du -sh data/qdrant/
python -c "from src.vector_store.qdrant_utils import qdrant_client, COLLECTION_NAME; info = qdrant_client.get_collection(COLLECTION_NAME); print(f'Vectors: {info.points_count}')"

# Test different search queries
python -c "from src.vector_store.qdrant_utils import search_similar_questions; results = search_similar_questions('satellite', filters={'topic': 'Science & Tech'}); print(f'Found {len(results)} results')"
```

### For Production
```bash
# Automated rebuild (can be added to cron jobs)
cd /path/to/tutor-backend
source scraper_env/bin/activate
python scripts/build_knowledge_base.py > build.log 2>&1
```

## 📚 Integration Examples

### Python API Usage
```python
from src.vector_store.qdrant_utils import search_similar_questions

# Basic search
results = search_similar_questions("What is India's GDP growth?", top_k=5)

# Topic-specific search
economy_questions = search_similar_questions(
    "economic indicators", 
    filters={"topic": "Economy"}, 
    top_k=10
)

# Difficulty-based search
easy_questions = search_similar_questions(
    "basic geography", 
    filters={"difficulty": "Easy"}, 
    top_k=5
)
```

### Web API Integration
```python
# Example FastAPI endpoint
from fastapi import FastAPI
from src.vector_store.qdrant_utils import search_similar_questions

app = FastAPI()

@app.get("/search")
async def search_questions(query: str, topic: str = None, top_k: int = 5):
    filters = {"topic": topic} if topic else None
    results = search_similar_questions(query, filters=filters, top_k=top_k)
    return {"query": query, "results": results}
``` 