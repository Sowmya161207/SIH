"""
ChatService: The integration bridge between the FastAPI POST /api/chat endpoint
and the AI Planner/Orchestration subsystem.
"""

import logging
from typing import Optional, List, Dict, Any

from .schemas import ChatRequest, ChatResponse, ExecutionPlan
from .planner_service import PlannerService, PlannerServiceError
from .orchestrator import Orchestrator, OrchestrationError

logger = logging.getLogger(__name__)


class ChatService:
    """
    Handles user chat requests by orchestrating:
    ChatRequest -> PlannerService -> Orchestrator -> ChatResponse
    """

    def __init__(
        self,
        planner_service: Optional[PlannerService] = None,
        orchestrator: Optional[Orchestrator] = None
    ):
        """
        :param planner_service: Configured PlannerService instance.
        :param orchestrator: Configured Orchestrator instance.
        """
        self.planner_service = planner_service or PlannerService()
        self.orchestrator = orchestrator or Orchestrator()

    async def process_chat(
        self,
        request: ChatRequest,
        document_ids: Optional[List[str]] = None
    ) -> ChatResponse:
        """
        Processes an incoming chat query through plan creation and orchestration.

        :param request: ChatRequest from POST /api/chat containing message and conversation_id.
        :param document_ids: Optional list of document IDs from context/session.
        :return: ChatResponse with answer, conversation_id, sources, and plan.
        """
        try:
            logger.info(f"Generating plan for query: '{request.message}'")
            
            # Step 1: Generate structured ExecutionPlan
            plan: ExecutionPlan = await self.planner_service.create_plan(query=request.message)
            logger.info(f"Created plan with intent='{plan.intent}', steps={len(plan.steps)}")

            # Step 2: Execute the plan through the Orchestrator
            response: ChatResponse = await self.orchestrator.execute_plan(
                plan=plan,
                original_query=request.message,
                conversation_id=request.conversation_id,
                document_ids=document_ids,
                user_role=request.user_role
            )

            return response


        except PlannerServiceError as pse:
            logger.error(f"Planning error for query '{request.message}': {pse}")
            return ChatResponse(
                answer=f"Unable to plan request: {str(pse)}",
                conversation_id=request.conversation_id,
                sources=[]
            )
        except OrchestrationError as oe:
            logger.error(f"Orchestration error for query '{request.message}': {oe}")
            return ChatResponse(
                answer=f"Execution error while fulfilling your request: {str(oe)}",
                conversation_id=request.conversation_id,
                sources=[]
            )
        except Exception as e:
            logger.critical(f"Unhandled exception in ChatService: {e}", exc_info=True)
            return ChatResponse(
                answer="An unexpected internal error occurred while processing your request.",
                conversation_id=request.conversation_id,
                sources=[]
            )
