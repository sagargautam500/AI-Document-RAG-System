
import json

from app.services.redis_service import get_redis_client


redis_client = get_redis_client()

CHAT_HISTORY_LIMIT = 10
CHAT_HISTORY_TTL = 86400


def get_chat_history(session_id: str) -> list[dict]:
    """Retrieve previous conversation messages from Redis."""

    key = f"chat:{session_id}"

    messages = redis_client.lrange(key, 0, -1)

    return [
        json.loads(message)
        for message in messages
    ]


def save_message(
    session_id: str,
    role: str,
    content: str
) -> None:
    """Save a conversation message in Redis."""

    key = f"chat:{session_id}"

    message = {
        "role": role,
        "content": content
    }

    redis_client.rpush(
        key,
        json.dumps(message)
    )

    # Keep only the latest 10 messages
    redis_client.ltrim(
        key,
        -CHAT_HISTORY_LIMIT,
        -1
    )

    # Automatically expire inactive sessions after 24 hours
    redis_client.expire(
        key,
        CHAT_HISTORY_TTL
    )


def clear_chat_history(session_id: str) -> None:
    """Delete conversation history from Redis."""

    redis_client.delete(f"chat:{session_id}")
