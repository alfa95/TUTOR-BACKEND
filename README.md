# Adaptive Quiz Engine

An intelligent quiz system that adapts to user performance using LLMs and vector search.

## 🚀 Features

- **Adaptive Learning**: Quiz difficulty adjusts based on user performance
- **RAG-powered Questions**: Uses retrieval-augmented generation for contextually relevant questions
- **User Progress Tracking**: MongoDB-based user session management
- **Vector Search**: Qdrant-based semantic search for knowledge retrieval
- **Multi-LLM Support**: Gemini and OpenAI integration

## 📋 Prerequisites

- Python 3.11+
- MongoDB (local or cloud)
- Qdrant Vector Database
- API keys for Gemini and OpenAI

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tutor-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.template .env
   # Edit .env with your actual API keys and database URLs
   ```

## 🔧 Configuration

### Environment Variables

Copy `env.template` to `.env` and configure:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `MONGO_URI`: MongoDB connection string
- `QDRANT_URL`: Qdrant vector database URL
- `JWT_SECRET_KEY`: Secret key for JWT tokens

### Database Setup

1. **MongoDB**: Set up local MongoDB or use MongoDB Atlas
2. **Qdrant**: Run locally with Docker or use Qdrant Cloud

```bash
# Local Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant
```

## 🚀 Running the Application

### Development Server
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Data Processing
```bash
# Build knowledge base
python scripts/build_knowledge_base.py

# Load data to Qdrant
python scripts/load_qdrant_batches.py
```

## 📁 Project Structure

```
tutor-backend/
├── src/
│   ├── api/           # FastAPI endpoints
│   ├── agents/        # LangGraph agents
│   ├── db/           # Database utilities
│   ├── llm/          # LLM integrations
│   ├── rag/          # RAG pipeline
│   └── vector_store/ # Vector database utilities
├── scripts/          # Data processing scripts
├── tests/           # Test suite
├── data/            # Knowledge base and processed data
├── deployment/      # Docker and deployment configs
└── notebooks/       # Jupyter notebooks for exploration
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_graph.py -v
```

## 🚀 Deployment

### Local with Docker
```bash
./deploy-local.sh
```

### Production
```bash
./deploy-prod.sh
```

### Railway Deployment
```bash
./deploy-railway.sh
```

## 🔒 Security Notes

- **Never commit API keys** to version control
- Use environment variables for all sensitive data
- Rotate JWT secrets regularly in production
- The `.gitignore` file excludes sensitive files automatically

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

[Add your license here]

