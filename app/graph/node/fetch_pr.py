from app.graph.state import GraphState
from app.services.github_service import GitHubService
from app.core.logger import logger


async def fetch_pr_node(state: GraphState) -> GraphState:
    """
    Node 0 — Fetches PR metadata and files from GitHub.
    Builds a formatted diff string for LLM consumption.
    """
    pr_number = state["pr_number"]
    logger.info(f"[fetch_pr] Fetching PR #{pr_number}")

    github = GitHubService()
    metadata = await github.get_pr_metadata(pr_number)
    files = await github.get_pr_files(pr_number)

    # Build a clean diff string for LLMs
    diff_parts = [
        f"PR #{metadata.pr_number}: {metadata.title}",
        f"Author: {metadata.author}",
        f"Branch: {metadata.head_branch} → {metadata.base_branch}",
        f"Files changed: {metadata.files_changed}",
        "=" * 60,
    ]
    for f in files:
        if f.patch:
            diff_parts.append(f"\n### File: {f.filename} ({f.status})")
            diff_parts.append(f.patch)

    diff_text = "\n".join(diff_parts)
    logger.info(f"[fetch_pr] Built diff | chars={len(diff_text)}")

    return {
        **state,
        "pr_metadata": metadata,
        "pr_files": files,
        "pr_diff_text": diff_text,
    }