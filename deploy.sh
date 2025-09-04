#!/bin/bash

echo "🚀 Deploying Interactive Learning System to GitHub Pages..."

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Get GitHub token
GITHUB_TOKEN=${GITHUB_TOKEN:-""}
if [ -z "$GITHUB_TOKEN" ]; then
    echo "�� GitHub Personal Access Token not found in environment."
    echo "💡 Please set GITHUB_TOKEN environment variable or enter it when prompted."
    read -s -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
    echo
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "❌ No token provided. Deployment cancelled."
        exit 1
    fi
fi

# Create temporary deployment directory
DEPLOY_DIR="deploy_temp"
if [ -d "$DEPLOY_DIR" ]; then
    rm -rf "$DEPLOY_DIR"
fi
mkdir "$DEPLOY_DIR"

# Copy files for deployment
echo "📁 Copying files for deployment..."
cp index.html "$DEPLOY_DIR/"
cp output/*.html "$DEPLOY_DIR/"
cp README.md "$DEPLOY_DIR/" 2>/dev/null || echo "README.md not found, skipping..."

# Create .nojekyll file
touch "$DEPLOY_DIR/.nojekyll"

# Navigate to deployment directory
cd "$DEPLOY_DIR"

# Initialize git repository
git init
git remote add origin "https://${GITHUB_TOKEN}@github.com/naveenpatil1/InteractiveLearning.git"

# Add and commit files
git add .
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Auto-deploy: Update Interactive Learning System - $TIMESTAMP"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin main --force

# Clean up
cd ..
rm -rf "$DEPLOY_DIR"

echo "✅ Deployment complete!"
echo "🌐 Your site is available at: https://naveenpatil1.github.io/InteractiveLearning/"
echo "⏱️  Changes will be live in 2-5 minutes"
