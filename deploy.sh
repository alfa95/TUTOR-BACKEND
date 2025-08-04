#!/bin/bash

# Deployment script for Tutor Backend
set -e

echo "🚀 Starting deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your configuration."
    exit 1
fi

# Build and deploy
echo "📦 Building Docker image..."
cd deployment
docker-compose -f docker-compose.prod.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful! API is running at http://localhost:8000"
    echo "📊 Health check: http://localhost:8000/health"
    echo "📚 API docs: http://localhost:8000/docs"
else
    echo "❌ Health check failed. Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

echo "🎉 Deployment completed!" 