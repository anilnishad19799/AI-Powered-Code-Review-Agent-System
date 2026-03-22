from typing import Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from operator import add
from app.models.schemas import (
    PRMetadata, PRFile,
    QualityReview, SecurityReview, PerformanceReview
)


def keep_last(existing, new):
    """Reducer: always keep the newest value. Used for fields written by parallel nodes."""
    return new if new is not None else existing


class GraphState(TypedDict):
    # ── Input (set once, never changed) ───────────────
    pr_number: int
    repo_full_name: str

    # ── Fetched PR Data (set by fetch_pr node only) ───
    pr_metadata: Optional[PRMetadata]
    pr_files: Optional[list[PRFile]]
    pr_diff_text: Optional[str]

    # ── Agent Outputs (each written by ONE agent) ─────
    # Use Annotated + keep_last so parallel writes don't conflict
    quality_review: Annotated[Optional[QualityReview], keep_last]
    security_review: Annotated[Optional[SecurityReview], keep_last]
    performance_review: Annotated[Optional[PerformanceReview], keep_last]

    # ── Final Output ───────────────────────────────────
    final_comment: Optional[str]

    # ── Control Flow ───────────────────────────────────
    error: Optional[str]
    messages: Annotated[list, add_messages]