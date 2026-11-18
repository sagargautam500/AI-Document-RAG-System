
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env file")


client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"


def generate_answer(
    question: str,
    context: str,
    chat_history: list[dict] | None = None
) -> str:
    """Generate an answer using Gemini and conversation history."""

    history_text = ""

    if chat_history:
        history_text = "\n".join(
            [
                f"{message['role']}: {message['content']}"
                for message in chat_history
            ]
        )

    prompt = f"""
You are a helpful document-based AI assistant.

Use the conversation history to understand follow-up questions.
Answer factual questions using ONLY the information in the
retrieved document context.

If the answer is not available in the retrieved context,
clearly say that the information was not found in the uploaded
documents. Do not make up information.

Previous Conversation:
{history_text}

Retrieved Document Context:
{context}

Current User Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()
