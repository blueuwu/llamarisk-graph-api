import time
import redis
from functools import wraps
from django.conf import settings

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

def rate_limit(max_requests=10, time_window=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"rate_limit:{func.__name__}"
            current_time = time.time()
            
            try:
                redis_client.zremrangebyscore(key, 0, current_time - time_window)

                request_count = redis_client.zcard(key)
                
                if request_count >= max_requests:
                    oldest_request = float(redis_client.zrange(key, 0, 0)[0].decode())
                    sleep_time = oldest_request + time_window - current_time
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                
                redis_client.zadd(key, {str(current_time): current_time})
                redis_client.expire(key, time_window)
                
                return func(*args, **kwargs)
                
            except redis.RedisError as e:
                print(f"Redis error in rate limiter: {e}")
                return func(*args, **kwargs)
                
        return wrapper
    return decorator