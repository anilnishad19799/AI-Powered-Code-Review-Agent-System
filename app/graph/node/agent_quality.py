from app.graph.state import GraphState
from app.services.llm.openai import OpenAIService
from app.models.schemas import QualityReview
from app.prompts.agent_prompts import QUALITY_AGENT_PROMPT
from app.core.logger import logger


async def agent_quality_node(state: GraphState) -> dict:
    logger.info("[agent_quality] Starting code quality review")
    llm = OpenAIService()

    result = await llm.complete_json(
        system_prompt=QUALITY_AGENT_PROMPT,
        user_message=f"Review this PR diff:\n\n{state['pr_diff_text']}",
    )

    review = QualityReview(**result)
    logger.info(f"[agent_quality] Score={review.score}/10 | Issues={len(review.issues)}")

    # ✅ Return ONLY what this agent owns — not {**state}
    return {"quality_review": review}