import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

for model in client.models.list():
    print(model.name)