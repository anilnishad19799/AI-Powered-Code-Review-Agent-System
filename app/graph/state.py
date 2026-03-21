from typing import Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from app.models.schemas import (
    PRMetadata, PRFile,
    QualityReview, SecurityReview, PerformanceReview
)


class GraphState(TypedDict):
    # ── Input ──────────────────────────────────────────
    pr_number: int

    # ── Fetched PR Data ────────────────────────────────
    pr_metadata: Optional[PRMetadata]
    pr_files: Optional[list[PRFile]]
    pr_diff_text: Optional[str]   # Formatted diff string for LLM

    # ── Agent Outputs ──────────────────────────────────
    quality_review: Optional[QualityReview]
    security_review: Optional[SecurityReview]
    performance_review: Optional[PerformanceReview]

    # ── Final Output ───────────────────────────────────
    final_comment: Optional[str]

    # ── Control Flow ───────────────────────────────────
    error: Optional[str]          # Set if any node fails
    messages: Annotated[list, add_messages]  # LangGraph message history