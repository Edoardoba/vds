#!/bin/bash

# Banta Frontend Deployment Script for Vercel

echo "🚀 Deploying Banta Frontend to Vercel..."

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the frontend directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the project
echo "🔨 Building project..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
else
    echo "❌ Build failed!"
    exit 1
fi

# Deploy to Vercel (requires Vercel CLI)
echo "🌐 Deploying to Vercel..."
if command -v vercel &> /dev/null; then
    vercel --prod
    echo "🎉 Deployment complete!"
    echo "📱 Check your app at: https://your-app.vercel.app"
else
    echo "⚠️  Vercel CLI not found. Install with: npm i -g vercel"
    echo "💡 Or deploy manually through Vercel Dashboard"
fi

echo "✅ Done!"
