#!/bin/bash

# Heroku deployment script for Freebies API

echo "🚀 Starting Heroku deployment..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run: heroku login"
    exit 1
fi

# Get app name from user
read -p "Enter your Heroku app name (or press Enter to create a new one): " APP_NAME

if [ -z "$APP_NAME" ]; then
    # Create new app
    echo "Creating new Heroku app..."
    APP_NAME=$(heroku create --json | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])")
    echo "✅ Created new app: $APP_NAME"
else
    # Check if app exists
    if ! heroku apps:info --app $APP_NAME &> /dev/null; then
        echo "❌ App '$APP_NAME' does not exist. Please create it first or use a different name."
        exit 1
    fi
    echo "✅ Using existing app: $APP_NAME"
fi

# Add PostgreSQL addon if not already added
echo "📦 Setting up PostgreSQL database..."
heroku addons:create heroku-postgresql:mini --app $APP_NAME 2>/dev/null || echo "PostgreSQL already configured"

# Set environment variables
echo "🔧 Setting up environment variables..."
heroku config:set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))") --app $APP_NAME
heroku config:set ALGORITHM=HS256 --app $APP_NAME
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30 --app $APP_NAME

# Get the database URL
DATABASE_URL=$(heroku config:get DATABASE_URL --app $APP_NAME)
echo "✅ Database URL configured"

# Run database migrations
echo "🗄️ Running database migrations..."
heroku run alembic upgrade head --app $APP_NAME

# Deploy the app
echo "📤 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku" || git commit -m "Update for Heroku deployment"
git push heroku main || git push heroku master

# Open the app
echo "🌐 Opening the deployed app..."
heroku open --app $APP_NAME

echo "✅ Deployment complete!"
echo "📊 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📋 API documentation: https://$APP_NAME.herokuapp.com/docs"
echo ""
echo "🔧 To view logs: heroku logs --tail --app $APP_NAME"
echo "🔧 To run commands: heroku run <command> --app $APP_NAME" 