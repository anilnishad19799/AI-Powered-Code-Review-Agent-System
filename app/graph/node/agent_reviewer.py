import json
from app.graph.state import GraphState
from app.services.llm.claude import ClaudeService
from app.services.github_service import GitHubService
from app.prompts.agent_prompts import REVIEWER_AGENT_PROMPT
from app.core.logger import logger


async def agent_reviewer_node(state: GraphState) -> GraphState:
    """
    Agent 4 — Synthesizes all 3 reviews into one GitHub comment.
    Also posts the comment to the PR.
    """
    logger.info("[agent_reviewer] Synthesizing final review")
    llm = ClaudeService()

    # Compile all agent results into one message
    combined = json.dumps({
        "quality": state["quality_review"].model_dump(),
        "security": state["security_review"].model_dump(),
        "performance": state["performance_review"].model_dump(),
        "pr_title": state["pr_metadata"].title,
        "pr_author": state["pr_metadata"].author,
    }, indent=2)

    final_comment = await llm.complete(
        system_prompt=REVIEWER_AGENT_PROMPT,
        user_message=f"Generate the final review comment:\n\n{combined}",
    )

    # Post to GitHub
    github = GitHubService()
    await github.post_review_comment(
        pr_number=state["pr_number"],
        comment=final_comment,
    )

    logger.info(f"[agent_reviewer] Final comment posted | PR #{state['pr_number']}")
    return {**state, "final_comment": final_comment}