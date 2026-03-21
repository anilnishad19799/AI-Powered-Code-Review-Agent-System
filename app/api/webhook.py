import json
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from arq import create_pool
from arq.connections import RedisSettings
from app.core.security import verify_github_signature
from app.core.config import get_settings
from app.core.logger import logger
from app.models.schemas import ReviewJobResponse, ReviewStatus

router = APIRouter()
settings = get_settings()


@router.post("/webhook", response_model=ReviewJobResponse)
async def github_webhook(request: Request):
    """
    Receives GitHub PR webhook events.
    Verifies signature → enqueues job → returns 202 immediately.
    """
    # Step 1 — Verify GitHub signature
    raw_body = await verify_github_signature(request)

    # Step 2 — Parse event type
    event_type = request.headers.get("X-GitHub-Event")
    if event_type != "pull_request":
        return {"message": "Event ignored", "status": "skipped"}

    payload = json.loads(raw_body)
    action = payload.get("action")

    # Only trigger on opened or synchronized (new commits pushed)
    if action not in ("opened", "synchronize"):
        logger.info(f"PR action '{action}' ignored")
        return ReviewJobResponse(
            job_id="skipped",
            pr_number=0,
            status=ReviewStatus.PENDING,
            message=f"Action '{action}' not handled",
        )

    pr_number = payload["pull_request"]["number"]
    logger.info(f"PR #{pr_number} {action} — enqueuing review job")

    # Step 3 — Enqueue background job (non-blocking)
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    job = await redis.enqueue_job("run_pr_review", pr_number)

    return ReviewJobResponse(
        job_id=job.job_id,
        pr_number=pr_number,
        status=ReviewStatus.PENDING,
        message="Review job enqueued successfully",
    )