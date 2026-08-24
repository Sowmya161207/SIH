"""
Sovereign AI Workbench - AI Planner and Orchestrator Package.
"""

from .schemas import (
    ActionType,
    TaskType,
    PlanStep,
    ExecutionPlan,
    PlannerResult,
    SourceMetadata,
    EvidenceItem,
    VerificationResult,
    RAGChunk,
    RAGResult,
    ChatRequest,
    ChatResponse
)
from .interfaces import (
    BasePlannerLLMClient,
    BaseRAGAgent,
    BaseVisionAgent,
    BaseAnalyticsAgent,
    BaseEvidenceVerifier,
    BaseLLMAgent,
    BaseWebSearchAgent
)
from .adapters import (
    MockPlannerLLMClient,
    MockRAGAgent,
    MockVisionAgent,
    MockAnalyticsAgent,
    MockEvidenceVerifier,
    MockLLMAgent,
    MockWebSearchAgent
)

from .planner_service import (
    PlannerService,
    PlannerServiceError,
    PlannerValidationError,
    PlannerExecutionError,
    plan_query
)
from .orchestrator import (
    Orchestrator,
    OrchestrationError
)
from .chat_service import ChatService
from .prompts import PLANNER_SYSTEM_PROMPT, build_planner_prompt

__all__ = [
    "ActionType",
    "TaskType",
    "PlanStep",
    "ExecutionPlan",
    "PlannerResult",
    "SourceMetadata",
    "EvidenceItem",
    "VerificationResult",
    "RAGChunk",
    "RAGResult",
    "ChatRequest",
    "ChatResponse",
    "BasePlannerLLMClient",
    "BaseRAGAgent",
    "BaseVisionAgent",
    "BaseAnalyticsAgent",
    "BaseEvidenceVerifier",
    "BaseLLMAgent",
    "BaseWebSearchAgent",
    "MockPlannerLLMClient",
    "MockRAGAgent",
    "MockVisionAgent",
    "MockAnalyticsAgent",
    "MockEvidenceVerifier",
    "MockLLMAgent",
    "MockWebSearchAgent",
    "PlannerService",
    "PlannerServiceError",
    "PlannerValidationError",
    "PlannerExecutionError",
    "plan_query",
    "Orchestrator",
    "OrchestrationError",
    "ChatService",
    "PLANNER_SYSTEM_PROMPT",
    "build_planner_prompt"
]

