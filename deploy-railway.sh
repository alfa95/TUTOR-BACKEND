#!/bin/bash

# Railway Deployment Helper Script
set -e

echo "🚂 Railway Deployment Helper"
echo "============================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "✅ Railway CLI found"

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

echo "✅ Logged in to Railway"

echo ""
echo "📋 Deployment Steps:"
echo "==================="
echo ""
echo "1. 🏗️  Create a new Railway project:"
echo "   railway init"
echo ""
echo "2. 🔧 Set environment variables in Railway dashboard:"
echo "   - Go to your project dashboard"
echo "   - Click on 'Variables' tab"
echo "   - Add all variables from railway.env.template"
echo ""
echo "3. 🚀 Deploy to Railway:"
echo "   railway up"
echo ""
echo "4. 🌐 Get your deployment URL:"
echo "   railway domain"
echo ""
echo "5. 📊 Check deployment status:"
echo "   railway status"
echo ""
echo "🔗 Useful Railway Commands:"
echo "=========================="
echo "railway logs          # View application logs"
echo "railway open          # Open deployment URL"
echo "railway variables     # View environment variables"
echo "railway connect       # Connect to database (if needed)"
echo ""

echo "📝 Important Notes:"
echo "=================="
echo "• Make sure your .env file has production values"
echo "• Update railway.json if you change the Dockerfile path"
echo "• Railway will automatically assign a PORT environment variable"
echo "• Your app will be available at: https://your-app-name.railway.app"
echo ""

echo "🎯 Ready to deploy? Run: railway up" 