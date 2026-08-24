"""
PlannerService: Core service responsible for interpreting queries, invoking the planner LLM,
parsing JSON responses safely, and validating ExecutionPlan Pydantic models.
"""

import json
import re
import logging
from typing import Optional, Dict, Any
from pydantic import ValidationError

import os
from .schemas import ExecutionPlan, PlanStep, PlannerResult
from .prompts import PLANNER_SYSTEM_PROMPT, build_planner_prompt
from .interfaces import BasePlannerLLMClient
from .adapters import MockPlannerLLMClient

logger = logging.getLogger(__name__)

# Default open-weight models mapped to capability tiers (configurable via env vars or code)
DEFAULT_MODEL_REGISTRY: Dict[str, str] = {
    "text": os.environ.get("TEXT_MODEL", "llama3:8b"),
    "vision": os.environ.get("VISION_MODEL", "llava:7b"),
    "multimodal": os.environ.get("MULTIMODAL_MODEL", "qwen-vl:7b"),
    "reasoning": os.environ.get("REASONING_MODEL", "qwen2.5-coder:7b"),
    "router": os.environ.get("ROUTER_MODEL", "llama3.2:3b"),
}


class PlannerServiceError(Exception):
    """Base exception for PlannerService failures."""
    pass


class PlannerValidationError(PlannerServiceError):
    """Raised when the query or generated plan fails schema validation."""
    pass


class PlannerExecutionError(PlannerServiceError):
    """Raised when the underlying LLM call or JSON parsing fails."""
    pass


class PlannerService:
    """
    Decoupled planning service that converts natural language queries into structured decisions
    and ExecutionPlans for the Backend and Orchestration subsystems.
    """

    def __init__(
        self,
        llm_client: Optional[BasePlannerLLMClient] = None,
        mode: Optional[str] = None,
        model_registry: Optional[Dict[str, str]] = None
    ):
        """
        :param llm_client: Implementation of BasePlannerLLMClient. Defaults to MockPlannerLLMClient.
        :param mode: Execution mode, e.g., 'mock' or 'llm'. Can also be set via PLANNER_MODE env var.
        :param model_registry: Optional capability-to-model mapping for local open-weight routing.
        """
        self.mode = mode or os.environ.get("PLANNER_MODE", "mock").lower()
        self.llm_client = llm_client or MockPlannerLLMClient()
        self.model_registry = {**DEFAULT_MODEL_REGISTRY, **(model_registry or {})}

    async def plan(
        self,
        query: str,
        conversation_id: Optional[str] = None
    ) -> PlannerResult:
        """
        Primary entry point for Backend integration (POST /api/chat).
        Evaluates the user query and returns a structured PlannerResult with task classification,
        modality requirements, and model capability routing.

        :param query: Natural language user query.
        :param conversation_id: Optional conversation tracking ID.
        :return: Structured PlannerResult containing action, task_type, requires_text, requires_image,
                 retrieval_required, selected_model, and granular execution steps.
        """
        # Guard: Empty or whitespace query (fail safely)
        if not query or not query.strip():
            return PlannerResult(
                action="clarification",
                task_type="clarification",
                query=query or "",
                requires_retrieval=False,
                retrieval_required=False,
                requires_generation=False,
                requires_text=False,
                requires_image=False,
                capability="text",
                selected_model=None,
                conversation_id=conversation_id,
                reason="Query is empty or whitespace only. Please provide a clear question or instruction."
            )

        cleaned_query = query.strip()
        lower_query = cleaned_query.lower()

        # Guard: Immediate clarification for ambiguous or underspecified queries
        ambiguous_phrases = {"tell me more", "tell me more.", "explain more", "more details", "what?", "why?", "tell me", "clarify", "more", "details"}
        if lower_query in ambiguous_phrases or lower_query.rstrip("?.!") in ambiguous_phrases:
            return PlannerResult(
                action="clarification",
                task_type="clarification",
                query=cleaned_query,
                requires_retrieval=False,
                retrieval_required=False,
                requires_generation=False,
                requires_text=False,
                requires_image=False,
                capability="text",
                selected_model=None,
                conversation_id=conversation_id,
                reason="Query is ambiguous or underspecified; requires clarification before execution."
            )

        try:
            execution_plan = await self.create_plan(cleaned_query)
            intent = execution_plan.intent

            # Map intent to SIH PS 26117 task types and capability routing
            if intent == "incident_investigation":
                task_type = "incident_investigation"
                action = "rag"
                requires_retrieval = True
                requires_generation = True
                requires_text = True
                requires_image = False
                requires_analytics = True
                capability = "reasoning"
                selected_model = self.model_registry.get("reasoning", "qwen2.5-coder:7b")
            elif intent == "maintenance_analytics":
                task_type = "maintenance_analytics"
                action = "rag"
                requires_retrieval = True
                requires_generation = True
                requires_text = True
                requires_image = False
                requires_analytics = True
                capability = "analytics"
                selected_model = self.model_registry.get("analytics", "qwen2.5-coder:7b")
            elif intent == "multimodal_qa":
                task_type = "multimodal_qa"
                action = "rag"
                requires_retrieval = True
                requires_generation = True
                requires_text = True
                requires_image = True
                requires_analytics = False
                capability = "multimodal"
                selected_model = self.model_registry.get("multimodal", "qwen-vl:7b")
            elif intent == "image_qa":
                task_type = "image_qa"
                action = "rag" if execution_plan.requires_rag else "direct_llm"
                requires_retrieval = execution_plan.requires_rag
                requires_generation = True
                requires_text = False
                requires_image = True
                requires_analytics = False
                capability = "vision"
                selected_model = self.model_registry.get("vision", "llava:7b")
            elif intent == "calculation_reasoning":
                task_type = "calculation_reasoning"
                action = "rag" if execution_plan.requires_rag else "direct_llm"
                requires_retrieval = execution_plan.requires_rag
                requires_generation = True
                requires_text = True
                requires_image = False
                requires_analytics = False
                capability = "reasoning"
                selected_model = self.model_registry.get("reasoning", "qwen2.5-coder:7b")
            elif intent in ("document_qa", "document_summarization", "document_comparison"):
                task_type = intent
                action = "rag"
                requires_retrieval = True
                requires_generation = True
                requires_text = True
                requires_image = False
                requires_analytics = False
                capability = "text"
                selected_model = self.model_registry.get("text", "llama3:8b")
            elif intent == "web_search_qa" or execution_plan.requires_web:
                task_type = "web_search_qa"
                action = "web_search"
                requires_retrieval = False
                requires_generation = True
                requires_text = True
                requires_image = False
                requires_analytics = False
                capability = "text"
                selected_model = self.model_registry.get("text", "llama3:8b")
            elif intent == "clarification":
                task_type = "clarification"
                action = "clarification"
                requires_retrieval = False
                requires_generation = False
                requires_text = False
                requires_image = False
                requires_analytics = False
                capability = "text"
                selected_model = None
            else:
                task_type = "general_qa"
                action = "direct_llm"
                requires_retrieval = False
                requires_generation = True
                requires_text = True
                requires_image = False
                requires_analytics = False
                capability = "text"
                selected_model = self.model_registry.get("text", "llama3:8b")

            return PlannerResult(
                action=action,
                task_type=task_type,
                query=cleaned_query,
                requires_retrieval=requires_retrieval,
                retrieval_required=requires_retrieval,
                requires_generation=requires_generation,
                requires_text=requires_text,
                requires_image=requires_image,
                requires_analytics=requires_analytics,
                capability=capability,
                selected_model=selected_model,
                conversation_id=conversation_id,
                reason=f"Plan generated for intent: '{execution_plan.intent}'",
                steps=execution_plan.steps
            )

        except Exception as e:
            logger.error(f"Planning error occurred during plan generation: {e}", exc_info=True)
            # Safe failure fallback to clarification (never crashes backend)
            return PlannerResult(
                action="clarification",
                task_type="clarification",
                query=cleaned_query,
                requires_retrieval=False,
                retrieval_required=False,
                requires_generation=False,
                requires_text=False,
                requires_image=False,
                requires_analytics=False,
                capability="text",
                selected_model=None,
                conversation_id=conversation_id,
                reason=f"Unable to determine unambiguous plan: {str(e)}"
            )



    async def create_plan(self, query: str) -> ExecutionPlan:
        """
        Creates an ExecutionPlan for a given user query.

        :param query: Natural language user query.
        :return: Validated ExecutionPlan.
        :raises PlannerValidationError: If query is invalid or plan schema is violated.
        :raises PlannerExecutionError: If planning LLM fails or returns unparseable output.
        """
        # 1. Validate query input
        if not query or not query.strip():
            raise PlannerValidationError("User query cannot be empty or whitespace only.")

        cleaned_query = query.strip()
        user_prompt = build_planner_prompt(cleaned_query)

        # 2. Call the planning LLM
        try:
            raw_response = await self.llm_client.complete(
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )
        except Exception as e:
            logger.error(f"Planner LLM invocation failed: {e}", exc_info=True)
            raise PlannerExecutionError(f"Failed to communicate with planning model: {str(e)}") from e

        # 3. Parse JSON from raw output
        plan_dict = self._parse_json_safely(raw_response)

        # 4. Validate through Pydantic Schema
        try:
            plan = ExecutionPlan.model_validate(plan_dict)
        except ValidationError as ve:
            logger.error(f"Plan validation failed against ExecutionPlan schema: {ve}")
            raise PlannerValidationError(f"ExecutionPlan schema validation failed: {ve}") from ve

        # 5. Validate Domain Invariants
        self._validate_plan_invariants(plan)

        return plan

    def _parse_json_safely(self, raw_text: str) -> Dict[str, Any]:
        """
        Extracts and parses JSON from raw LLM output, discarding markdown code fences
        or surrounding conversational commentary.
        """
        text = raw_text.strip()

        # Remove markdown code fences ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if fence_match:
            text = fence_match.group(1).strip()

        # Fallback regex to find outermost JSON braces if extra text surrounds JSON
        brace_match = re.search(r"\{[\s\S]*\}", text)
        if brace_match:
            text = brace_match.group(0)

        try:
            return json.loads(text)
        except json.JSONDecodeError as jde:
            logger.error(f"JSON decode failed on text:\n{raw_text}\nError: {jde}")
            raise PlannerExecutionError(f"Planning model output could not be parsed as JSON: {str(jde)}") from jde

    def _validate_plan_invariants(self, plan: ExecutionPlan) -> None:
        """
        Verifies domain-specific invariants:
        - Steps must be non-empty and 1-indexed sequential.
        - Supported tools must be recognized ('rag', 'vision', 'analytics', 'verify', 'llm', 'web_search').
        - Final step must be an 'llm' tool.
        - If requires_rag is True, 'rag' tool must appear before 'llm'.
        """
        if not plan.steps:
            raise PlannerValidationError("ExecutionPlan must contain at least one step.")

        valid_tools = {"rag", "vision", "analytics", "verify", "llm", "web_search"}
        rag_seen = False

        for idx, step in enumerate(plan.steps, start=1):
            if step.tool not in valid_tools:
                raise PlannerValidationError(f"Step {step.step} references unsupported tool '{step.tool}'.")

            if step.tool == "rag":
                rag_seen = True

        # Ensure final step uses LLM for response synthesis
        if plan.steps[-1].tool != "llm":
            raise PlannerValidationError(f"Final step of ExecutionPlan must use 'llm' tool for answer generation, got '{plan.steps[-1].tool}'.")

        # Ensure requires_rag consistency
        if plan.requires_rag and not rag_seen:
            raise PlannerValidationError("Plan specifies requires_rag=True but contains no RAG step.")
