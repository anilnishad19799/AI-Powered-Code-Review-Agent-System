from app.graph.state import GraphState
from app.services.llm.openai import OpenAIService
from app.models.schemas import PerformanceReview
from app.prompts.agent_prompts import PERFORMANCE_AGENT_PROMPT
from app.core.logger import logger


async def agent_performance_node(state: GraphState) -> dict:
    logger.info("[agent_performance] Starting performance review")
    llm = OpenAIService()

    result = await llm.complete_json(
        system_prompt=PERFORMANCE_AGENT_PROMPT,
        user_message=f"Review this PR diff:\n\n{state['pr_diff_text']}",
    )

    review = PerformanceReview(**result)
    logger.info(f"[agent_performance] Score={review.score}/10 | Issues={len(review.improvements)}")

    # ✅ Return ONLY what this agent owns
    return {"performance_review": review}