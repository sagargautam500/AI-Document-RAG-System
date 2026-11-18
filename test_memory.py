
from app.services.memory_service import (
    save_message,
    get_chat_history,
    clear_chat_history
)


session_id = "test-session-001"

# Save user message
save_message(
    session_id,
    "user",
    "What is Python?"
)

# Save AI response
save_message(
    session_id,
    "assistant",
    "Python is a programming language."
)

# Retrieve conversation
history = get_chat_history(session_id)

print("Conversation History:")

for message in history:
    print(message)

# Cleanup test data
clear_chat_history(session_id)

print("Memory test completed!")
