# 🚀 Deployment Guide

This project supports two deployment modes: **Local Development** and **Production with Cloud Databases**.

## 🏠 Local Development (Everything Local)

Use this for development, testing, and when you want everything running locally.

### Quick Start:
```bash
./deploy-local.sh
```

### What it includes:
- ✅ **Local Qdrant** (Docker container)
- ✅ **Local MongoDB** (Docker container) 
- ✅ **API Server** (Docker container)
- ✅ **Volume mounts** for live code changes
- ✅ **All data stored locally**

### URLs:
- **API**: http://localhost:8000
- **Qdrant**: http://localhost:6333
- **MongoDB**: localhost:27017
- **API Docs**: http://localhost:8000/docs

### Stop Local Environment:
```bash
cd deployment
docker-compose -f docker-compose.local.yml down
```

---

## ☁️ Production (Cloud Databases)

Use this for production deployment with cloud databases.

### Quick Start:
```bash
./deploy-prod.sh
```

### What it includes:
- ✅ **Qdrant Cloud** (https://cloud.qdrant.io)
- ✅ **MongoDB Atlas** (Cloud database)
- ✅ **API Server** (Docker container)
- ✅ **Production optimized** settings

### Requirements:
- `.env` file with cloud database URLs
- Qdrant Cloud account
- MongoDB Atlas account

### URLs:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Databases**: Cloud-hosted

### Stop Production Environment:
```bash
cd deployment
docker-compose -f docker-compose.prod.yml down
```

---

## 🔧 Environment Configuration

### Local Development (.env.local):
```bash
# Local databases
QDRANT_URL=http://localhost:6333
MONGO_URI=mongodb://admin:password@localhost:27017

# Your API keys
GEMINI_API_KEY=your-key
OPENAI_API_KEY=your-key
```

### Production (.env):
```bash
# Cloud databases
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-api-key
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net

# Your API keys
GEMINI_API_KEY=your-key
OPENAI_API_KEY=your-key
```

---

## 📊 Comparison

| Feature | Local | Production |
|---------|-------|------------|
| **Qdrant** | Local Docker | Qdrant Cloud |
| **MongoDB** | Local Docker | MongoDB Atlas |
| **Data Persistence** | Docker volumes | Cloud storage |
| **Scalability** | Single instance | Cloud scalable |
| **Cost** | Free | Pay per use |
| **Development** | ✅ Live code changes | ❌ Rebuild required |
| **Production** | ❌ Not suitable | ✅ Production ready |

---

## 🛠️ Manual Commands

### Local Development:
```bash
# Start local environment
cd deployment
docker-compose -f docker-compose.local.yml up -d

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Stop
docker-compose -f docker-compose.local.yml down
```

### Production:
```bash
# Start production environment
cd deployment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

---

## 🔍 Troubleshooting

### Check if databases are connected:
```bash
# Check Qdrant
curl http://localhost:6333/collections

# Check MongoDB (if local)
docker exec deployment-mongodb-1 mongosh --eval "db.adminCommand('ping')"

# Check API health
curl http://localhost:8000/health
```

### View container logs:
```bash
# API logs
docker logs deployment-api-1

# Qdrant logs (local)
docker logs deployment-qdrant-1

# MongoDB logs (local)
docker logs deployment-mongodb-1
``` 