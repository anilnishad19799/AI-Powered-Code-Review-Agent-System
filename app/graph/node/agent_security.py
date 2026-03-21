from app.graph.state import GraphState
from app.services.llm.claude import ClaudeService
from app.models.schemas import SecurityReview
from app.prompts.agent_prompts import SECURITY_AGENT_PROMPT
from app.core.logger import logger


async def agent_security_node(state: GraphState) -> GraphState:
    logger.info("[agent_security] Starting security review")
    llm = ClaudeService()

    result = await llm.complete_json(
        system_prompt=SECURITY_AGENT_PROMPT,
        user_message=f"Review this PR diff:\n\n{state['pr_diff_text']}",
    )

    review = SecurityReview(**result)
    logger.info(f"[agent_security] Score={review.score}/10 | Vulns={len(review.vulnerabilities)}")
    return {**state, "security_review": review}