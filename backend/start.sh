#!/bin/bash
# Startup script for AI Startup

echo "=========================================="
echo "AI Startup - Starting up..."
echo "=========================================="

# Check if GROQ_API_KEY is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  WARNING: GROQ_API_KEY is not set!"
    echo ""
    echo "To fix this:"
    echo "1. Go to https://railway.app/dashboard"
    echo "2. Select your AI_Startup project"
    echo "3. Go to Variables"
    echo "4. Add GROQ_API_KEY with your Groq API key"
    echo ""
    echo "Get your API key from: https://console.groq.com/keys"
    echo ""
    echo "The application will start but AI features won't work."
    echo "=========================================="
else
    echo "✅ GROQ_API_KEY is set"
    echo "✅ Starting application..."
fi

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
