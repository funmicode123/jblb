from django.core.cache import cache
from django.http import JsonResponse
import time

RATE_LIMIT = 60
WINDOW = 60

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR")
        key = f"rl:{ip}"

        data = cache.get(key)

        now = time.time()

        if data:
            count, start = data
            if now - start < WINDOW:
                if count >= RATE_LIMIT:
                    return JsonResponse(
                        {"detail": "Too many requests"},
                        status=429
                    )
                cache.set(key, (count + 1, start), WINDOW)
            else:
                cache.set(key, (1, now), WINDOW)
        else:
            cache.set(key, (1, now), WINDOW)

        return self.get_response(request)
