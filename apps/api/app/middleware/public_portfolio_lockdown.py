from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config.settings import settings

BLOCKED_RESPONSE = JSONResponse(
    status_code=404,
    content={"detail": "Not found."},
)

ALLOWED_ROUTES: frozenset[tuple[str, str]] = frozenset(
    {
        ("GET", "/health"),
        ("GET", "/api/v1/health/ready"),
        ("OPTIONS", "/api/v1/public/portfolio/chat"),
        ("POST", "/api/v1/public/portfolio/chat"),
    }
)

BLOCKED_DOC_PATHS: frozenset[str] = frozenset(
    {
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)


def normalize_path(path: str) -> str:
    if path != "/" and path.endswith("/"):
        return path.rstrip("/")
    return path


def is_public_portfolio_route_allowed(method: str, path: str) -> bool:
    normalized_path = normalize_path(path)
    normalized_method = method.upper()

    if normalized_path in BLOCKED_DOC_PATHS:
        return False

    if normalized_path.startswith("/docs/"):
        return False

    return (normalized_method, normalized_path) in ALLOWED_ROUTES


def public_portfolio_lockdown_response(
    *,
    public_portfolio_mode: bool,
    method: str,
    path: str,
) -> Response | None:
    if not public_portfolio_mode:
        return None

    if is_public_portfolio_route_allowed(method, path):
        return None

    return BLOCKED_RESPONSE


class PublicPortfolioLockdownMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        blocked = public_portfolio_lockdown_response(
            public_portfolio_mode=settings.public_portfolio_mode,
            method=request.method,
            path=request.url.path,
        )
        if blocked is not None:
            return blocked

        return await call_next(request)
