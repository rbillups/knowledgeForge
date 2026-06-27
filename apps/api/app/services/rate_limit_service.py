import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.config.settings import settings


class InMemoryRateLimiter:
    """Simple process-local rate limiter for first-deployment safeguards."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def reset(self) -> None:
        self._events.clear()

    def _client_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    def check(self, request: Request) -> None:
        now = time.monotonic()
        client_key = self._client_key(request)
        events = self._events[client_key]

        while events and now - events[0] >= self.window_seconds:
            events.popleft()

        if len(events) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Too many chat requests. Please wait a few minutes and try again."
                ),
            )

        events.append(now)


chat_rate_limiter = InMemoryRateLimiter(
    max_requests=settings.chat_rate_limit_max_requests,
    window_seconds=settings.chat_rate_limit_window_seconds,
)


def enforce_chat_rate_limit(request: Request) -> None:
    chat_rate_limiter.check(request)
