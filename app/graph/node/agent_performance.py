from app.graph.state import GraphState
from app.services.llm.claude import ClaudeService
from app.models.schemas import PerformanceReview
from app.prompts.agent_prompts import PERFORMANCE_AGENT_PROMPT
from app.core.logger import logger


async def agent_performance_node(state: GraphState) -> GraphState:
    logger.info("[agent_performance] Starting performance review")
    llm = ClaudeService()

    result = await llm.complete_json(
        system_prompt=PERFORMANCE_AGENT_PROMPT,
        user_message=f"Review this PR diff:\n\n{state['pr_diff_text']}",
    )

    review = PerformanceReview(**result)
    logger.info(f"[agent_performance] Score={review.score}/10 | Issues={len(review.improvements)}")
    return {**state, "performance_review": review}