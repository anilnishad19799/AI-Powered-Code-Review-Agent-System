"""
Why this exists:
GitHub expects a webhook response within 10 seconds.
A full 4-agent review takes 30-60 seconds.
Solution: Immediately return 202 Accepted, run review in background via ARQ + Redis.
"""
from arq import ArqRedis
from app.graph.builder import review_graph
from app.graph.state import GraphState
from app.core.config import get_settings
from app.core.logger import logger

settings = get_settings()


async def run_pr_review(ctx: dict, pr_number: int) -> dict:
    """
    ARQ worker function — runs inside Redis job queue.
    Called by webhook handler, not directly by FastAPI.
    """
    logger.info(f"[worker] Starting review job for PR #{pr_number}")

    initial_state: GraphState = {
        "pr_number": pr_number,
        "pr_metadata": None,
        "pr_files": None,
        "pr_diff_text": None,
        "quality_review": None,
        "security_review": None,
        "performance_review": None,
        "final_comment": None,
        "error": None,
        "messages": [],
    }

    try:
        final_state = await review_graph.ainvoke(initial_state)
        logger.info(f"[worker] Review completed for PR #{pr_number}")
        return {"status": "completed", "pr_number": pr_number}
    except Exception as e:
        logger.error(f"[worker] Review failed for PR #{pr_number}: {e}")
        return {"status": "failed", "pr_number": pr_number, "error": str(e)}


# ARQ worker settings
from arq.connections import RedisSettings
class WorkerSettings:
    # redis_settings = settings.redis_url
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [run_pr_review]
    max_jobs = 10
    job_timeout = 300  # 5 minutes max per review