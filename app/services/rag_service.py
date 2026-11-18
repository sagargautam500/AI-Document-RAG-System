
from datetime import date, time

from app.services.retrieval_service import search_similar_chunks
from app.services.llm_service import generate_answer

from app.services.memory_service import (
    get_chat_history,
    save_message
)

from app.services.booking_service import (
    detect_booking_intent,
    extract_booking_details,
    get_missing_booking_field,
    save_interview_booking
)


def ask_question(
    question: str,
    session_id: str,
    limit: int = 5
) -> dict:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    # Step 1: Retrieve previous conversation
    chat_history = get_chat_history(session_id)

    # Step 2: Detect whether this is an interview booking request
    is_booking = detect_booking_intent(
        message=question,
        chat_history=chat_history
    )

    # ------------------------------------------------
    # INTERVIEW BOOKING PIPELINE
    # ------------------------------------------------

    if is_booking:

        # Step 3: Extract booking information
        details = extract_booking_details(
            message=question,
            chat_history=chat_history
        )

        # Validate extracted date and time
        try:
            if details.get("interview_date"):
                date.fromisoformat(details["interview_date"])
        except ValueError:
            details["interview_date"] = None

        try:
            if details.get("interview_time"):
                time.fromisoformat(details["interview_time"])
        except ValueError:
            details["interview_time"] = None

        # Basic email validation
        email = details.get("email")

        if email and (
            "@" not in email or "." not in email.split("@")[-1]
        ):
            details["email"] = None

        # Step 4: Check for missing information
        missing_question = get_missing_booking_field(details)

        if missing_question:

            answer = missing_question

            save_message(session_id, "user", question)
            save_message(session_id, "assistant", answer)

            return {
                "session_id": session_id,
                "type": "interview_booking",
                "booking_status": "collecting_details",
                "question": question,
                "answer": answer,
                "booking_details": details,
                "sources": []
            }

        # Step 5: Save complete booking into PostgreSQL
        booking = save_interview_booking(
            session_id=session_id,
            details=details
        )

        answer = (
            "Your interview booking has been successfully "
            "recorded. Here are your booking details:\n"
            f"Name: {booking['name']}\n"
            f"Email: {booking['email']}\n"
            f"Date: {booking['interview_date']}\n"
            f"Time: {booking['interview_time']}\n"
            f"Booking ID: {booking['booking_id']}"
        )

        save_message(session_id, "user", question)
        save_message(session_id, "assistant", answer)

        return {
            "session_id": session_id,
            "type": "interview_booking",
            "booking_status": "confirmed",
            "question": question,
            "answer": answer,
            "booking": booking,
            "sources": []
        }

    # ------------------------------------------------
    # NORMAL RAG PIPELINE
    # ------------------------------------------------

    # Step 3: Build contextual search query
    history_context = "\n".join(
        [
            f"{message['role']}: {message['content']}"
            for message in chat_history
        ]
    )

    contextual_query = (
        f"{history_context}\nuser: {question}"
        if history_context
        else question
    )

    # Step 4: Retrieve relevant document chunks
    retrieved_chunks = search_similar_chunks(
        query=contextual_query,
        limit=limit
    )

    # Step 5: Build document context
    context = "\n\n".join(
        [
            f"Document: {chunk['filename']}\n"
            f"Chunk ID: {chunk['chunk_id']}\n"
            f"Content: {chunk['text']}"
            for chunk in retrieved_chunks
        ]
    )

    # Step 6: Generate answer using Gemini
    if retrieved_chunks:
        answer = generate_answer(
            question=question,
            context=context,
            chat_history=chat_history
        )
    else:
        answer = (
            "No relevant information was found "
            "in the uploaded documents."
        )

    # Step 7: Save conversation in Redis
    save_message(session_id, "user", question)
    save_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "type": "document_chat",
        "question": question,
        "answer": answer,
        "sources": [
            {
                "filename": chunk["filename"],
                "chunk_id": chunk["chunk_id"],
                "score": chunk["score"]
            }
            for chunk in retrieved_chunks
        ]
    }
