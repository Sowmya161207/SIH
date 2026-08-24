"""
Abstract interfaces for RAG, LLM, Web Search, and Planner LLM integrations.
These enable zero coupling between the Orchestrator/Planner and specific third-party libraries.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .schemas import RAGResult, SourceMetadata


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
    """Abstract interface for document retrieval services owned by the RAG engineer."""

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        """
        Retrieves relevant document chunks and source citations.

        :param query: Search query or topic to retrieve.
        :param document_ids: Optional list of specific document IDs to restrict search to.
        :param filters: Optional additional search filters.
        :return: RAGResult containing chunks and source metadata.
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
        :param context: List of context strings (e.g., retrieved RAG text chunks).
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
