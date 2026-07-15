"""Startup validation for AI Startup."""
import os
import sys

print("=" * 60)
print("AI Startup - Startup Validation")
print("=" * 60)

# Check Groq API Key
groq_key = os.getenv("GROQ_API_KEY", "")
if groq_key:
    print(f"✅ GROQ_API_KEY is set (length: {len(groq_key)})")
    print(f"   Prefix: {groq_key[:15]}...")
else:
    print("❌ GROQ_API_KEY is NOT set")
    print("   Will use fallback key from config.py")

# Check other important variables
print(f"
LLM_MODE: {os.getenv('LLM_MODE', 'not set')}")
print(f"PORT: {os.getenv('PORT', 'not set')}")
print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'not set')}")

print("=" * 60)
