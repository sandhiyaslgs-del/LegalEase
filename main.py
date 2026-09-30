import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai


# =========================================================
# LOAD .ENV
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=api_key
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="LegalEase API"
)


# =========================================================
# REQUEST MODEL
# =========================================================

class LegalRequest(BaseModel):

    document_type: str

    details: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to LegalEase API"
    }


# =========================================================
# GENERATE LEGAL DOCUMENT
# =========================================================

@app.post("/generate")
def generate_document(
    request: LegalRequest
):

    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are a professional legal document drafting assistant.

Create a professional draft legal document.

Document Type:
{request.document_type}

Party and Agreement Details:
{request.details}

Instructions:

1. Create a clear and professional document.
2. Start with a suitable title.
3. Include the names of Party A and Party B.
4. Include the effective date if provided.
5. Convert the Terms & Conditions into suitable numbered clauses.
6. Add appropriate standard clauses where necessary.
7. Include a signature section for both parties.
8. Do not invent personal information.
9. Do not create fake addresses, phone numbers,
   email addresses, or identification numbers.
10. Use simple but professional legal language.
11. Return ONLY the document content.
12. Do not use markdown code blocks.
13. This document is an AI-generated draft and should
    be reviewed by a qualified legal professional.
"""


    # -----------------------------------------------------
    # GEMINI MODEL
    # -----------------------------------------------------

    model_name = "gemini-3.5-flash"


    try:

        print(
            f"Generating document using: {model_name}"
        )


        # -------------------------------------------------
        # GEMINI REQUEST
        # -------------------------------------------------

        response = client.models.generate_content(

            model=model_name,

            contents=prompt
        )


        # -------------------------------------------------
        # GET GENERATED TEXT
        # -------------------------------------------------

        generated_text = response.text


        # -------------------------------------------------
        # CHECK RESPONSE
        # -------------------------------------------------

        if not generated_text:

            raise HTTPException(
                status_code=500,
                detail="Gemini returned an empty response."
            )


        generated_text = generated_text.strip()


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        print(
            "Document generated successfully."
        )


        return {

            "document_type": request.document_type,

            # IMPORTANT:
            # Frontend expects "document"
            "document": generated_text,

            "model_used": model_name
        }


    # -----------------------------------------------------
    # GEMINI ERROR
    # -----------------------------------------------------

    except HTTPException:

        raise


    except Exception as e:

        print(
            f"Gemini Error: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail=f"Document generation failed: {str(e)}"
        )