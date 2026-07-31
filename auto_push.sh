#!/bin/bash

# ==============================================================================
# Automatic Git Sync & Push Script for SudPay
# Target Account: wleedmhamed086-art
# Repository: sudpay-engine
# ==============================================================================

echo "🚀 Starting SudPay Auto-Sync & Deployment Script..."

# 1. Configure Git Credentials for wleedmhamed086-art
git config user.name "wleedmhamed086-art"
echo "✅ Set Git User: wleedmhamed086-art"

# Ask for Git email if not set globally
CURRENT_EMAIL=$(git config user.email)
if [ -z "$CURRENT_EMAIL" ]; then
    read -p "Enter your GitHub email address: " USER_EMAIL
    git config user.email "$USER_EMAIL"
fi

# 2. Initialize repository if not already initialized
if [ ! -d ".git" ]; then
    git init
    git branch -M main
    echo "✅ Initialized Git Repository (main branch)"
fi

# 3. Ensure Remote Origin is linked to wleedmhamed086-art/sudpay-engine
REMOTE_URL="https://github.com/wleedmhamed086-art/sudpay-engine.git"
if git remote | grep -q "^origin$"; then
    git remote set-url origin $REMOTE_URL
else
    git remote add origin $REMOTE_URL
fi
echo "🔗 Remote URL configured: $REMOTE_URL"

# 4. Stage and Commit All Files
git add .
COMMIT_MSG="Auto-update SudPay Engine - $(date +'%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG" || echo "ℹ️ No changes to commit."

# 5. Push to GitHub
echo "📤 Pushing code to https://github.com/wleedmhamed086-art/sudpay-engine..."
git push -u origin main

echo "🎉 Success! SudPay Ecosystem is fully updated on your GitHub repository."
