from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────
class ReviewStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    REVIEWER = "reviewer"


class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── PR Data ────────────────────────────────────────────────────────────────────
class PRMetadata(BaseModel):
    pr_number: int
    title: str
    author: str
    base_branch: str
    head_branch: str
    repo_full_name: str
    files_changed: int
    additions: int
    deletions: int
    pr_url: str


class PRFile(BaseModel):
    filename: str
    status: str                  # added, modified, removed
    additions: int
    deletions: int
    patch: Optional[str] = None  # The actual diff


# ── Agent Output Models ────────────────────────────────────────────────────────
class CodeIssue(BaseModel):
    file: str
    line: Optional[int] = None
    severity: IssueSeverity
    description: str
    suggestion: str


class QualityReview(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Code quality score 0-10")
    issues: list[CodeIssue] = []
    summary: str
    passed: bool


class SecurityReview(BaseModel):
    score: int = Field(..., ge=0, le=10)
    vulnerabilities: list[CodeIssue] = []
    summary: str
    passed: bool


class PerformanceReview(BaseModel):
    score: int = Field(..., ge=0, le=10)
    improvements: list[CodeIssue] = []
    summary: str
    passed: bool


# ── Webhook Payload ────────────────────────────────────────────────────────────
class GitHubWebhookPayload(BaseModel):
    action: str
    number: int
    pull_request: dict


# ── API Response ───────────────────────────────────────────────────────────────
class ReviewJobResponse(BaseModel):
    job_id: str
    pr_number: int
    status: ReviewStatus
    message: str