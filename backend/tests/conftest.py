"""Pytest configuration and shared fixtures."""
import pytest
import os

# Set test environment variables before importing app
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("JWT_SECRET", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "test")
