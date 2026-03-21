from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


# ── Base ───────────────────────────────────────────────────────────────────────
class PRReviewBaseException(Exception):
    """Root exception. All custom exceptions inherit from this."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ── GitHub ─────────────────────────────────────────────────────────────────────
class GitHubAPIException(PRReviewBaseException):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(f"GitHub API error: {message}", status_code)


class PRNotFoundException(PRReviewBaseException):
    def __init__(self, pr_number: int):
        super().__init__(f"PR #{pr_number} not found", status_code=404)


# ── Agent ──────────────────────────────────────────────────────────────────────
class AgentExecutionException(PRReviewBaseException):
    def __init__(self, agent_name: str, reason: str):
        super().__init__(
            f"Agent '{agent_name}' failed: {reason}", status_code=500
        )


class LLMResponseParseException(PRReviewBaseException):
    def __init__(self, agent_name: str, raw_response: str):
        self.raw_response = raw_response
        super().__init__(
            f"Agent '{agent_name}' returned unparseable JSON", status_code=500
        )


# ── Webhook ────────────────────────────────────────────────────────────────────
class WebhookVerificationException(PRReviewBaseException):
    def __init__(self):
        super().__init__("Webhook signature verification failed", status_code=403)


# ── Worker ─────────────────────────────────────────────────────────────────────
class WorkerJobException(PRReviewBaseException):
    def __init__(self, job_id: str, reason: str):
        super().__init__(f"Worker job '{job_id}' failed: {reason}", status_code=500)


# ── Global FastAPI exception handler ──────────────────────────────────────────
async def global_exception_handler(
    request: Request, exc: PRReviewBaseException
) -> JSONResponse:
    logger.error(
        f"Handled exception | path={request.url.path} | "
        f"type={type(exc).__name__} | message={exc.message}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "path": str(request.url.path),
        },
    )