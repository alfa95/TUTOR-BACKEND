#!/bin/bash

# Production Deployment Script (Cloud Databases)
set -e

echo "☁️ Starting PRODUCTION deployment with cloud databases..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env file exists with cloud config
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your cloud database configuration."
    exit 1
fi

# Verify cloud database URLs are set
if ! grep -q "QDRANT_URL=https://" .env; then
    echo "❌ QDRANT_URL not set to cloud URL in .env"
    exit 1
fi

if ! grep -q "MONGO_URI=mongodb+srv://" .env; then
    echo "❌ MONGO_URI not set to Atlas URL in .env"
    exit 1
fi

echo "✅ Cloud database configuration verified"

# Build and deploy
echo "📦 Building Docker image..."
cd deployment
docker-compose -f docker-compose.prod.yml build

echo "🚀 Starting production API (using cloud databases)..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Production deployment successful!"
    echo "🌐 API: http://localhost:8000"
    echo "📊 Health: http://localhost:8000/health"
    echo "📚 Docs: http://localhost:8000/docs"
    echo "☁️ Using: Qdrant Cloud + MongoDB Atlas"
else
    echo "❌ Health check failed. Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

echo "🎉 Production environment ready!" 