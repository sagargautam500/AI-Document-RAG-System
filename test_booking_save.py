
from app.services.booking_service import save_interview_booking

details = {
    "name": "Sagar Gautam",
    "email": "sagar@example.com",
    "interview_date": "2026-11-25",
    "interview_time": "10:00"
}

result = save_interview_booking(
    session_id="sagar-session-001",
    details=details
)

print("\nInterview Booking Saved Successfully!")
print(result)
