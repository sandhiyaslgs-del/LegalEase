import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import errors


# =========================
# Load .env
# =========================

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")


# =========================
# Gemini Client
# =========================

client = genai.Client(api_key=api_key)


# =========================
# FastAPI App
# =========================

app = FastAPI(title="LegalEase API")


# =========================
# Request Model
# =========================

class LegalRequest(BaseModel):
    document_type: str
    details: str


# =========================
# Home
# =========================

@app.get("/")
def home():
    return {
        "message": "Welcome to LegalEase API"
    }


# =========================
# Generate Document
# =========================

@app.post("/generate")
def generate_document(request: LegalRequest):

    prompt = f"""
You are a legal document drafting assistant.

Create a professional draft of the following document:

Document Type:
{request.document_type}

Details:
{request.details}

Requirements:
- Use clear and professional language.
- Organize the document with suitable headings.
- Include important clauses where appropriate.
- Do not invent personal information that was not provided.
- This is a draft document and should be reviewed by a qualified legal professional.
"""

    # Try available models one by one
    models = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash"
    ]

    last_error = None

    for model_name in models:

        try:
            print(f"Trying Gemini model: {model_name}")

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            if response.text:
                print(f"SUCCESS: {model_name}")

                return {
                    "document_type": request.document_type,
                    "generated_document": response.text,
                    "model_used": model_name
                }

        except errors.ServerError as e:

            last_error = e

            print(f"GEMINI ERROR with {model_name}: {e}")

            # Try next model
            continue

        except Exception as e:

            last_error = e

            print(f"ERROR with {model_name}: {e}")

            # Try next model
            continue


    # If all models fail
    raise HTTPException(
        status_code=503,
        detail=f"Document generation failed. Gemini models are currently unavailable. Error: {last_error}"
    )