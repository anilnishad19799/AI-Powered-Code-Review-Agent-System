from app.graph.state import GraphState
from app.services.llm.claude import ClaudeService
from app.models.schemas import QualityReview
from app.prompts.agent_prompts import QUALITY_AGENT_PROMPT
from app.core.logger import logger


async def agent_quality_node(state: GraphState) -> GraphState:
    logger.info("[agent_quality] Starting code quality review")
    llm = ClaudeService()

    result = await llm.complete_json(
        system_prompt=QUALITY_AGENT_PROMPT,
        user_message=f"Review this PR diff:\n\n{state['pr_diff_text']}",
    )

    review = QualityReview(**result)
    logger.info(f"[agent_quality] Score={review.score}/10 | Issues={len(review.issues)}")
    return {**state, "quality_review": review}