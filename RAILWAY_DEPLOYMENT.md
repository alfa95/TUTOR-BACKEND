# 🚂 Railway Deployment Guide

This guide will help you deploy your Tutor Backend to Railway.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install with `npm install -g @railway/cli`
3. **Git Repository**: Your code should be in a Git repository
4. **Cloud Databases**: Qdrant Cloud and MongoDB Atlas configured

## 🚀 Quick Deployment

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway
```bash
railway login
```

### Step 3: Initialize Railway Project
```bash
railway init
```

### Step 4: Set Environment Variables
Go to your Railway dashboard and add these environment variables:

```bash
# Database Configuration
MONGO_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=Users
MONGO_USER_COLLECTION=user
MONGO_QUIZ_COLLECTION=quiz_sessions

# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

# LLM API Keys
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# JWT Secret (generate a strong secret)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

### Step 5: Deploy
```bash
railway up
```

### Step 6: Get Your URL
```bash
railway domain
```

## 🔧 Configuration Files

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "deployment/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Dockerfile (deployment/Dockerfile)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./src ./src

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (Railway will set PORT environment variable)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run the application (Railway will override PORT)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails**
   ```bash
   # Check build logs
   railway logs
   
   # Common fixes:
   # - Ensure all dependencies are in requirements.txt
   # - Check Dockerfile path in railway.json
   ```

2. **Environment Variables Not Set**
   ```bash
   # Check variables
   railway variables
   
   # Set variables via CLI
   railway variables set MONGO_URI="your-mongo-uri"
   ```

3. **Health Check Fails**
   ```bash
   # Check if app is running
   railway logs
   
   # Verify health endpoint
   curl https://your-app.railway.app/health
   ```

4. **Database Connection Issues**
   ```bash
   # Check if databases are accessible
   # Ensure IP whitelist includes Railway's IPs
   # Verify connection strings
   ```

### Useful Commands

```bash
# View logs
railway logs

# Open deployment URL
railway open

# Check status
railway status

# View variables
railway variables

# Redeploy
railway up

# Get domain
railway domain
```

## 📊 Monitoring

### Railway Dashboard
- **Deployments**: View deployment history
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory usage
- **Variables**: Environment configuration

### Health Checks
Your app includes a health check endpoint:
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-04T18:52:58.044500"
}
```

## 🔄 Continuous Deployment

### GitHub Integration
1. Connect your GitHub repository to Railway
2. Railway will automatically deploy on pushes to main branch
3. Set up branch protection rules for production

### Manual Deployment
```bash
# Deploy current branch
railway up

# Deploy specific branch
railway up --branch feature-branch
```

## 💰 Cost Optimization

### Railway Pricing
- **Free Tier**: $5/month credit
- **Pay-as-you-go**: $0.000463 per second
- **Pro**: $20/month for unlimited usage

### Optimization Tips
1. **Use Free Tier**: Perfect for development/testing
2. **Scale Down**: Stop unused deployments
3. **Monitor Usage**: Check Railway dashboard regularly
4. **Optimize Build**: Reduce Docker image size

## 🎯 Production Checklist

- [ ] Environment variables set correctly
- [ ] Database connections working
- [ ] Health checks passing
- [ ] SSL certificate active
- [ ] Domain configured
- [ ] Monitoring set up
- [ ] Logs accessible
- [ ] Backup strategy in place

## 🆘 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: For code-specific issues

## 🎉 Success!

Once deployed, your API will be available at:
```
https://your-app-name.railway.app
```

Test your endpoints:
- Health: `GET /health`
- API Docs: `GET /docs`
- Query: `POST /query` 