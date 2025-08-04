#!/bin/bash

# Local Development Deployment Script
set -e

echo "🏠 Starting LOCAL development deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Copy local environment
echo "📝 Setting up local environment..."
cp env.local .env

# Build and deploy
echo "📦 Building Docker image..."
cd deployment
docker-compose -f docker-compose.local.yml build

echo "🚀 Starting local services (Qdrant + MongoDB + API)..."
docker-compose -f docker-compose.local.yml up -d

echo "⏳ Waiting for services to start..."
sleep 15

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Local deployment successful!"
    echo "🌐 API: http://localhost:8000"
    echo "📊 Health: http://localhost:8000/health"
    echo "📚 Docs: http://localhost:8000/docs"
    echo "🗄️  Qdrant: http://localhost:6333"
    echo "🍃 MongoDB: localhost:27017"
else
    echo "❌ Health check failed. Check logs with: docker-compose -f docker-compose.local.yml logs"
    exit 1
fi

echo "🎉 Local development environment ready!" 