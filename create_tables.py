from app.database.connection import Base, engine
from app.models import Document
from app.models.interview_booking import InterviewBooking

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")