import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_MODEL_NAME = "openai/gpt-oss-120b"

def call_llm(prompt: str) -> str:
    """Send a prompt to Groq and return the raw text response."""

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Check your .env file.")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    return response.choices[0].message.content