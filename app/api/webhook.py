import json
import hashlib
import hmac
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.logger import logger

# ⚠️ No response_model here — we return JSONResponse directly
# This gives us full control over what we return
router = APIRouter()
settings = get_settings()


@router.post("/webhook")
async def github_webhook(request: Request):
    """
    GitHub webhook receiver.
    
    Flow:
    1. Read raw body
    2. Verify HMAC signature
    3. Parse event type
    4. Ignore non-PR events
    5. Enqueue review job for opened/synchronize PRs
    """

    # ── 1. Read raw body ───────────────────────────────────────────────────────
    try:
        raw_body = await request.body()
    except Exception as e:
        logger.error(f"Failed to read body: {e}")
        return JSONResponse(status_code=400, content={"error": "Cannot read body"})

    # ── 2. Verify GitHub HMAC signature ───────────────────────────────────────
    signature_header = request.headers.get("X-Hub-Signature-256", "")

    if signature_header:
        expected_sig = (
            "sha256="
            + hmac.new(
                settings.github_webhook_secret.encode("utf-8"),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
        )
        if not hmac.compare_digest(expected_sig, signature_header):
            logger.warning("❌ Webhook signature mismatch")
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid signature"}
            )

    logger.info("✅ Signature verified")

    # ── 3. Parse JSON payload ──────────────────────────────────────────────────
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    # ── 4. Read headers ────────────────────────────────────────────────────────
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    action     = payload.get("action", "unknown")
    pr_number  = payload.get("number", 0)

    logger.info(f"📥 Event received | type={event_type} | action={action} | PR=#{pr_number}")

    # ── 5. Handle ping (sent when webhook is first created) ───────────────────
    if event_type == "ping":
        logger.info("🏓 GitHub ping — webhook connected successfully!")
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "message": "Webhook connected! Ping received from GitHub."
            }
        )

    # ── 6. Ignore everything except pull_request ──────────────────────────────
    if event_type != "pull_request":
        logger.info(f"⏭️  Ignoring event: {event_type}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "ignored",
                "message": f"Event type '{event_type}' is not handled"
            }
        )

    # ── 7. Only care about opened / synchronize / reopened ────────────────────
    if action not in ("opened", "synchronize", "reopened"):
        logger.info(f"⏭️  Ignoring PR action: {action}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "ignored",
                "message": f"PR action '{action}' does not trigger review"
            }
        )

    # ── 8. Enqueue background review job ──────────────────────────────────────
    logger.info(f"🚀 Triggering review for PR #{pr_number}")

    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        job   = await redis.enqueue_job("run_pr_review", pr_number)
        await redis.aclose()

        logger.info(f"✅ Job enqueued | job_id={job.job_id} | PR=#{pr_number}")

        return JSONResponse(
            status_code=202,
            content={
                "status":    "accepted",
                "message":   "Review job enqueued successfully",
                "pr_number": pr_number,
                "job_id":    job.job_id,
            }
        )

    except Exception as e:
        logger.error(f"❌ Failed to enqueue job: {type(e).__name__}: {e}")

        # Still return 200 so GitHub doesn't retry endlessly
        return JSONResponse(
            status_code=200,
            content={
                "status":    "received",
                "message":   "PR event received but job queue unavailable",
                "pr_number": pr_number,
                "error":     str(e),
            }
        )