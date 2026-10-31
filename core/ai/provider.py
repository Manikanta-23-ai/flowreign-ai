
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class AIProviderError(Exception):
    pass


def generate_text(prompt: str) -> str:
    """Generate text using the configured Gemini model."""

    if not API_KEY:
        raise AIProviderError(
            "GEMINI_API_KEY is missing. Configure it in the project .env file."
        )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent"
    )

    try:
        response = requests.post(
            url,
            params={"key": API_KEY},
            json={
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1800,
                },
            },
            timeout=90,
        )

        response.raise_for_status()
        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except requests.RequestException as error:
        raise AIProviderError(
            f"Gemini API request failed: {error}"
        ) from error
    except (KeyError, IndexError, TypeError) as error:
        raise AIProviderError(
            "The AI provider returned an unexpected response."
        ) from error
