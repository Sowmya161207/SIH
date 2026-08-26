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

    def __init__(self, llm_client: Optional[BasePlannerLLMClient] = None, mode: Optional[str] = None):
        """
        :param llm_client: Implementation of BasePlannerLLMClient. Defaults to MockPlannerLLMClient.
        :param mode: Execution mode, e.g., 'mock' or 'llm'. Can also be set via PLANNER_MODE env var.
        """
        self.mode = mode or os.environ.get("PLANNER_MODE", "mock").lower()
        if llm_client:
            self.llm_client = llm_client
        elif self.mode == "llm":
            from .ollama_client import OllamaPlannerLLMClient
            self.llm_client = OllamaPlannerLLMClient()
        else:
            self.llm_client = MockPlannerLLMClient()

    async def plan(
        self,
        query: str,
        conversation_id: Optional[str] = None
    ) -> PlannerResult:
        """
        Primary entry point for Backend integration (POST /api/chat).
        Evaluates the user query and returns a structured PlannerResult.

        :param query: Natural language user query.
        :param conversation_id: Optional conversation tracking ID.
        :return: Structured PlannerResult containing action, requires_retrieval, requires_generation, etc.
        """
        # Guard: Empty or whitespace query
        if not query or not query.strip():
            return PlannerResult(
                action="clarification",
                query=query or "",
                requires_retrieval=False,
                requires_generation=False,
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
                query=cleaned_query,
                requires_retrieval=False,
                requires_generation=False,
                conversation_id=conversation_id,
                reason="Query is ambiguous or underspecified; requires clarification before execution."
            )

        try:
            execution_plan = await self.create_plan(cleaned_query)
            
            # Map execution plan to primary action
            if execution_plan.requires_rag:
                action = "rag"
                requires_retrieval = True
                requires_generation = True
            elif execution_plan.requires_web:
                action = "web_search"
                requires_retrieval = False
                requires_generation = True
            elif execution_plan.intent == "clarification":
                action = "clarification"
                requires_retrieval = False
                requires_generation = False
            else:
                action = "direct_llm"
                requires_retrieval = False
                requires_generation = True

            return PlannerResult(
                action=action,
                query=cleaned_query,
                requires_retrieval=requires_retrieval,
                requires_generation=requires_generation,
                conversation_id=conversation_id,
                reason=f"Plan generated for intent: '{execution_plan.intent}'",
                steps=execution_plan.steps
            )

        except Exception as e:
            logger.error(f"Planning error occurred during plan generation: {e}", exc_info=True)
            # Predictable fallback to clarification
            return PlannerResult(
                action="clarification",
                query=cleaned_query,
                requires_retrieval=False,
                requires_generation=False,
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
        plan_dict = self._extract_json(raw_response)

        # 4. Validate against Pydantic ExecutionPlan schema
        try:
            plan = ExecutionPlan.model_validate(plan_dict)
        except ValidationError as ve:
            logger.error(f"ExecutionPlan schema validation error: {ve}", exc_info=True)
            raise PlannerValidationError(f"Generated plan violates schema: {str(ve)}") from ve

        # 5. Post-validation checks on plan structure
        self._validate_plan_invariants(plan)

        return plan

    def _extract_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Robustly extracts JSON from an LLM response string, handling markdown fences and extraneous text.
        """
        if not raw_text or not raw_text.strip():
            raise PlannerExecutionError("Planning model returned an empty response.")

        text = raw_text.strip()

        # Check for ```json ... ``` code fence
        json_fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if json_fence_match:
            text = json_fence_match.group(1).strip()

        # Extract outer curly braces if extra text exists
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
        - Supported tools must be recognized ('rag', 'llm', 'web_search').
        - Final step must be an 'llm' tool.
        - If requires_rag is True, 'rag' tool must appear before 'llm'.
        """
        if not plan.steps:
            raise PlannerValidationError("ExecutionPlan must contain at least one step.")

        valid_tools = {"rag", "llm", "web_search"}
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
