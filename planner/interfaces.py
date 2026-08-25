"""
Abstract interfaces for RAG, Vision, Analytics, Evidence Verification, LLM, and Planner LLM integrations.
These enable zero coupling between the Orchestrator/Planner and specific third-party libraries.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .schemas import RAGResult, SourceMetadata, EvidenceItem, VerificationResult


class BasePlannerLLMClient(ABC):
    """Abstract interface for calling an LLM to generate the raw plan JSON."""

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends the planning prompt to the LLM and returns the raw response text.
        
        :param system_prompt: The instructions and schema.
        :param user_prompt: The formatted user query.
        :return: Raw string response (typically a JSON string).
        """
        pass


class BaseRAGAgent(ABC):
    """
    Abstract interface for document retrieval services owned by the RAG engineer.
    The Planner interacts strictly through search_documents / retrieve.
    """

    @abstractmethod
    async def search_documents(
        self,
        query: str,
        user_role: Optional[str] = None,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        """
        Retrieves relevant document chunks and source citations.

        :param query: Search query or topic to retrieve.
        :param user_role: Optional role of the requesting user for access control.
        :param top_k: Maximum number of chunks to return.
        :param document_ids: Optional list of specific document IDs to restrict search to.
        :param filters: Optional additional search filters.
        :return: RAGResult containing chunks and source metadata.
        """
        pass

    async def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        """Backward-compatible alias for search_documents."""
        return await self.search_documents(
            query=query,
            document_ids=document_ids,
            filters=filters
        )


class BaseVisionAgent(ABC):
    """
    Abstract interface for Vision / Multimodal analysis of P&ID diagrams, schematics, and blueprints.
    Owned by the Multimodal / Vision engineer.
    """

    @abstractmethod
    async def analyze_image(
        self,
        query: str,
        image_path: Optional[str] = None,
        image_data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Analyzes an image, P&ID diagram, or engineering drawing according to query.

        :param query: Inspection query or instruction.
        :param image_path: Path or identifier of the image file.
        :param image_data: Raw image bytes or base64 data if available.
        :return: Dict containing extracted observations, detected components, and confidence.
        """
        pass

    async def analyze_document_image(
        self,
        query: str,
        document_id: Optional[str] = None,
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        """Extracts and analyzes a diagram from a specific document page."""
        return await self.analyze_image(query=query, image_path=document_id)


class BaseAnalyticsAgent(ABC):
    """
    Abstract interface for Telemetry and Maintenance Analytics.
    Owned by the Data Analytics team.
    """

    @abstractmethod
    async def get_maintenance_analytics(
        self,
        equipment_id: Optional[str] = None,
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves maintenance history, sensor telemetry statistics, and anomaly detections.

        :param equipment_id: Identifier of the asset/equipment (e.g. 'P-101', 'C-200').
        :param query: Query string describing analytics required.
        :param parameters: Optional extra parameters (time window, sensor thresholds).
        :return: Dict containing telemetry stats, anomaly flags, and recommended actions.
        """
        pass

    async def analyze_telemetry(
        self,
        equipment_id: str,
        sensor_types: Optional[List[str]] = None,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convenience method for telemetry analysis."""
        return await self.get_maintenance_analytics(
            equipment_id=equipment_id,
            query=time_range,
            parameters={"sensor_types": sensor_types} if sensor_types else None
        )


class BaseEvidenceVerifier(ABC):
    """
    Abstract interface for Evidence Verification and Hallucination Guard.
    Ensures that generated answers are grounded in retrieved facts and flags insufficient evidence.
    """

    @abstractmethod
    async def verify_evidence(
        self,
        query: str,
        evidence: List[EvidenceItem],
        answer: Optional[str] = None
    ) -> VerificationResult:
        """
        Evaluates whether the collected evidence sufficiently and reliably grounds the query answer.

        :param query: The original user question.
        :param evidence: List of collected EvidenceItem instances from RAG, Vision, Analytics.
        :param answer: Optional draft answer to verify for factual consistency.
        :return: VerificationResult indicating sufficiency, confidence, and validation status.
        """
        pass


class BaseLLMAgent(ABC):
    """Abstract interface for synthesis, generation, summarization, and comparison."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[List[str]] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generates answers, summaries, comparisons, or reasoning.

        :param prompt: Main user prompt or task instruction.
        :param context: List of context strings (e.g., retrieved RAG text chunks, telemetry, visual notes).
        :param system_instruction: Optional specialized system instructions.
        :return: Synthesized answer string.
        """
        pass


class BaseWebSearchAgent(ABC):
    """Abstract interface for optional external web search."""

    @abstractmethod
    async def search(self, query: str, num_results: int = 3) -> List[str]:
        """
        Searches the web for recent external information.

        :param query: Search query string.
        :param num_results: Maximum number of snippets to return.
        :return: List of retrieved web text snippets.
        """
        pass

