
import os

API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
API_BASE = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-sdlcassist")
