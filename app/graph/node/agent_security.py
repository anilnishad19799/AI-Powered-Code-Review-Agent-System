from app.graph.state import GraphState
from app.services.llm.openai import OpenAIService
from app.models.schemas import SecurityReview
from app.prompts.agent_prompts import SECURITY_AGENT_PROMPT
from app.core.logger import logger


async def agent_security_node(state: GraphState) -> dict:
    logger.info("[agent_security] Starting security review")
    llm = OpenAIService()

    result = await llm.complete_json(
        system_prompt=SECURITY_AGENT_PROMPT,
        user_message=f"Review this PR diff:\n\n{state['pr_diff_text']}",
    )

    review = SecurityReview(**result)
    logger.info(f"[agent_security] Score={review.score}/10 | Vulns={len(review.vulnerabilities)}")

    # ✅ Return ONLY what this agent owns
    return {"security_review": review}