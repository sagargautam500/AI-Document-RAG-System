
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.llm_service import client, MODEL_NAME
from datetime import date, time


def extract_booking_details(
    message: str,
    chat_history: list[dict] | None = None
) -> dict:

    # Convert previous conversation into text
    history_text = ""

    if chat_history:
        history_text = "\n".join(
            f"{item['role']}: {item['content']}"
            for item in chat_history
        )

    # Get current date in Nepal timezone
    current_date = datetime.now(
        ZoneInfo("Asia/Kathmandu")
    ).date().isoformat()

    # Gemini prompt
    prompt = f"""
You are an interview booking information extraction assistant.

Current date: {current_date}

Extract the following information from the user's message
and previous conversation:

1. name
2. email
3. interview_date
4. interview_time

Rules:
- Use previous conversation to understand follow-up messages.
- Extract only information explicitly provided by the user.
- Do not invent or assume any information.
- If a field is unavailable, return null.
- Date format must be YYYY-MM-DD.
- Time format must be 24-hour HH:MM.
- Resolve relative dates using the current date when clear.
- If a date or time is ambiguous, return null.
- Return valid JSON only.
- Do not include Markdown or code fences.

Previous conversation:
{history_text}

Current user message:
{message}

Required JSON structure:
{{
    "name": null,
    "email": null,
    "interview_date": null,
    "interview_time": null
}}
"""

    # Generate response using Gemini
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty extraction response."
        )

    # Parse Gemini JSON response
    try:
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "")
            response_text = response_text.replace("```", "")
            response_text = response_text.strip()

        details = json.loads(response_text)

    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Gemini returned invalid JSON: {response.text}"
        ) from error

    # Return only required fields
    required_fields = [
        "name",
        "email",
        "interview_date",
        "interview_time"
    ]

    return {
        field: details.get(field)
        for field in required_fields
    }


def get_missing_booking_field(details: dict) -> str | None:

    field_questions = {
        "name": "May I know your full name?",
        "email": "Could you please provide your email address?",
        "interview_date": "What date would you prefer for the interview? (YYYY-MM-DD)",
        "interview_time": "What time would you prefer for the interview? (HH:MM)"
    }

    for field, question in field_questions.items():
        if not details.get(field):
            return question

    return None


from app.database.connection import SessionLocal
from app.models.interview_booking import InterviewBooking


def save_interview_booking(
    session_id: str,
    details: dict
) -> dict:

    db = SessionLocal()

    try:
        booking = InterviewBooking(
            session_id=session_id,
            name=details["name"],
            email=details["email"],
            interview_date=date.fromisoformat(details["interview_date"]),
            interview_time=time.fromisoformat(details["interview_time"])
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return {
            "booking_id": booking.id,
            "session_id": booking.session_id,
            "name": booking.name,
            "email": booking.email,
            "interview_date": booking.interview_date.isoformat(),
            "interview_time": booking.interview_time.strftime("%H:%M"),
            "status": "confirmed"
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()



def detect_booking_intent(
    message: str,
    chat_history: list[dict] | None = None
) -> bool:

    history_text = ""

    if chat_history:
        history_text = "\n".join(
            f"{item['role']}: {item['content']}"
            for item in chat_history
        )

    prompt = f"""
You are an intent classification assistant.

Determine whether the user wants to book an interview.

Return JSON only:
{{"is_booking_request": true}}

Rules:
- Return true if the user explicitly wants to book or schedule an interview.
- Return true if the user is providing information requested
  during an ongoing interview booking conversation.
- Return false for normal questions about documents,
  resumes, skills, education, or other general topics.
- Return false if the previous booking was already confirmed
  and the user is not requesting another booking.
- Do not assume booking intent from unrelated messages.

Previous conversation:
{history_text}

Current user message:
{message}

Return:
{{"is_booking_request": true}}
or
{{"is_booking_request": false}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty intent response."
        )

    try:
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "")
            response_text = response_text.replace("```", "")
            response_text = response_text.strip()

        result = json.loads(response_text)

    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Invalid intent classification JSON: {response.text}"
        ) from error

    return result.get("is_booking_request") is True
