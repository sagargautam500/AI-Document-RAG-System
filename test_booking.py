
from app.services.booking_service import extract_booking_details

message = """
My name is Sagar Gautam.
My email is sagar@example.com.
I want to book an interview on November 25, 2026 at 10 AM.
"""

result = extract_booking_details(message)

print("\nExtracted Interview Details:")
print(result)
