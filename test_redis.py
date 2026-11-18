from app.services.redis_service import test_redis_connection

if test_redis_connection():
    print("Redis connected successfully!")