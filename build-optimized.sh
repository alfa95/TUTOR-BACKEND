#!/bin/bash

echo "🐳 Building optimized Docker image..."

# Build the optimized image
cd deployment
docker build -f Dockerfile.optimized -t tutor-backend:optimized ..

echo "✅ Optimized image built successfully!"
echo "📊 Image size comparison:"
echo ""

# Show image sizes
docker images | grep tutor-backend || echo "No previous images found for comparison"

echo ""
echo "🚀 To run the optimized image:"
echo "   docker-compose -f docker-compose.optimized.yml up -d"
echo ""
echo "🔍 To check the image layers and size:"
echo "   docker history tutor-backend:optimized" 