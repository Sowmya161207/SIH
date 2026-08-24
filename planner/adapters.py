"""
Concrete adapters and mock implementations of the agent interfaces.
Provides ready-to-run mocks for testing/demos as well as pluggable HTTP adapters.
"""

import json
import re
from typing import List, Optional, Dict, Any
from .interfaces import BasePlannerLLMClient, BaseRAGAgent, BaseLLMAgent, BaseWebSearchAgent
from .schemas import RAGResult, RAGChunk, SourceMetadata


class MockPlannerLLMClient(BasePlannerLLMClient):
    """
    Deterministic rule-based planning LLM mock for unit testing and offline demo execution.
    Can also be overridden with custom response fixtures.
    """

    def __init__(self, override_response: Optional[str] = None):
        self.override_response = override_response

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        if self.override_response:
            return self.override_response

        # Extract clean query if user_prompt contains wrapper template
        clean_query = user_prompt.strip()
        match = re.search(r"User query:\s*(.*?)(?:\n\s*Generate the execution plan JSON:|$)", user_prompt, re.DOTALL | re.IGNORECASE)
        if match:
            clean_query = match.group(1).strip()

        lower_query = clean_query.lower()

        # Ambiguous / underspecified queries
        ambiguous_triggers = ["tell me more", "tell me more.", "explain more", "more details", "what?", "why?", "tell me", "clarify", "help me"]
        if lower_query in ambiguous_triggers or lower_query.rstrip("?.!") in ambiguous_triggers or lower_query in ["more", "why", "what", "how", "details"]:
            plan_dict = {
                "intent": "clarification",
                "requires_rag": False,
                "requires_web": False,
                "steps": [
                    {
                        "step": 1,
                        "tool": "llm",
                        "action": "clarify",
                        "input": "Could you clarify what you would like me to explain further?"
                    }
                ]
            }
        # Multimodal QA (cross-referencing document text/specs AND P&ID/diagrams/images)
        elif any(img in lower_query for img in ["p&id", "pid", "diagram", "drawing", "schematic", "image", "blueprint"]) and \
             re.search(r"\b(document|documents|pdf|specification|specifications|specs|report|reports|text|manual|datasheet|compare)\b", lower_query):

            plan_dict = {
                "intent": "multimodal_qa",
                "requires_rag": True,
                "requires_web": False,
                "steps": [
                    {
                        "step": 1,
                        "tool": "rag",
                        "action": "retrieve",
                        "input": clean_query
                    },
                    {
                        "step": 2,
                        "tool": "llm",
                        "action": "synthesize",
                        "input": "Synthesize cross-modal response combining document text and visual diagram annotations."
                    }
                ]
            }
        # Image / P&ID QA (Diagrams, blueprints, piping & instrumentation drawings)
        elif any(img in lower_query for img in ["p&id", "pid", "piping and instrumentation", "diagram", "blueprint", "schematic", "drawing", "flowsheet", "valve symbol", "image", "photo", "tag number", "instrument loop"]):
            plan_dict = {
                "intent": "image_qa",
                "requires_rag": True,
                "requires_web": False,
                "steps": [
                    {
                        "step": 1,
                        "tool": "rag",
                        "action": "retrieve",
                        "input": clean_query
                    },
                    {
                        "step": 2,
                        "tool": "llm",
                        "action": "synthesize",
                        "input": "Analyze visual components and annotations in the diagram/P&ID."
                    }
                ]
            }
        # Calculation / Quantitative Reasoning
        elif any(k in lower_query for k in ["calculate", "compute", "formula", "flow rate", "pressure drop", "mass balance", "heat duty", "unit conversion", "math", "equation", "solve for", "derive"]):
            requires_rag = any(doc in lower_query for doc in ["document", "pdf", "uploaded", "file", "table", "datasheet"])
            steps = []
            if requires_rag:
                steps.append({
                    "step": 1,
                    "tool": "rag",
                    "action": "retrieve",
                    "input": clean_query
                })
                steps.append({
                    "step": 2,
                    "tool": "llm",
                    "action": "calculate",
                    "input": "Perform calculations using parameters retrieved from the document."
                })
            else:
                steps.append({
                    "step": 1,
                    "tool": "llm",
                    "action": "calculate",
                    "input": clean_query
                })
            plan_dict = {
                "intent": "calculation_reasoning",
                "requires_rag": requires_rag,
                "requires_web": False,
                "steps": steps
            }
        # Document comparison
        elif "compare" in lower_query and ("document" in lower_query or "pdf" in lower_query or "architecture" in lower_query or "uploaded" in lower_query):
            plan_dict = {
                "intent": "document_comparison",
                "requires_rag": True,
                "requires_web": False,
                "steps": [
                    {
                        "step": 1,
                        "tool": "rag",
                        "action": "retrieve",
                        "input": clean_query
                    },
                    {
                        "step": 2,
                        "tool": "llm",
                        "action": "compare",
                        "input": "Compare the retrieved document sections, highlighting similarities, differences, strengths, and weaknesses."
                    }
                ]
            }
        # Document summarization
        elif "summarize" in lower_query or "summary" in lower_query:
            plan_dict = {
                "intent": "document_summarization",
                "requires_rag": True,
                "requires_web": False,
                "steps": [
                    {
                        "step": 1,
                        "tool": "rag",
                        "action": "retrieve",
                        "input": clean_query
                    },
                    {
                        "step": 2,
                        "tool": "llm",
                        "action": "summarize",
                        "input": "Summarize the key findings, conclusions, and core concepts from the retrieved content."
                    }
                ]
            }
        # Document Q&A (uploaded / pdf / document / security mechanisms / policy / etc.)
        elif any(k in lower_query for k in ["pdf", "document", "uploaded", "file", "security mechanism", "policy", "report", "manual", "spec"]):
            plan_dict = {
                "intent": "document_qa",
                "requires_rag": True,
                "requires_web": False,
                "steps": [
                    {
                        "step": 1,
                        "tool": "rag",
                        "action": "retrieve",
                        "input": clean_query
                    },
                    {
                        "step": 2,
                        "tool": "llm",
                        "action": "synthesize",
                        "input": "Synthesize a grounded answer based strictly on the retrieved document chunks."
                    }
                ]
            }
        # Web Search
        elif any(k in lower_query for k in ["latest", "current", "news", "today", "recent development", "web"]):
            plan_dict = {
                "intent": "web_search_qa",
                "requires_rag": False,
                "requires_web": True,
                "steps": [
                    {
                        "step": 1,
                        "tool": "web_search",
                        "action": "search",
                        "input": clean_query
                    },
                    {
                        "step": 2,
                        "tool": "llm",
                        "action": "synthesize",
                        "input": "Synthesize a response using the retrieved web search results."
                    }
                ]
            }
        # General Knowledge QA
        else:
            plan_dict = {
                "intent": "general_qa",
                "requires_rag": False,
                "requires_web": False,
                "steps": [
                    {
                        "step": 1,
                        "tool": "llm",
                        "action": "answer",
                        "input": clean_query
                    }
                ]
            }


        return json.dumps(plan_dict, indent=2)


class MockRAGAgent(BaseRAGAgent):
    """
    Mock RAG Agent simulating retrieval of document chunks with rich metadata.
    """

    def __init__(self, sample_document: str = "security_architecture.pdf", sample_page: int = 12):
        self.sample_document = sample_document
        self.sample_page = sample_page

    async def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        doc_name = (document_ids[0] if document_ids and len(document_ids) > 0 else self.sample_document)
        chunk1 = RAGChunk(
            text="The Sovereign AI system implements zero-trust access control with hardware-backed encryption modules.",
            source=SourceMetadata(document=doc_name, page=self.sample_page, chunk_id="chunk_001", score=0.92)
        )
        chunk2 = RAGChunk(
            text="All data transfers within the enclave are authenticated using mTLS and verified against policy constraints.",
            source=SourceMetadata(document=doc_name, page=self.sample_page + 1, chunk_id="chunk_002", score=0.88)
        )
        return RAGResult(
            chunks=[chunk1, chunk2],
            sources=[chunk1.source, chunk2.source]
        )


class MockLLMAgent(BaseLLMAgent):
    """
    Mock LLM Agent simulating synthesis, summarization, and answer generation.
    Deterministic and query-aware for testing and offline execution.
    """

    async def generate(
        self,
        prompt: str,
        context: Optional[List[str]] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        prompt_lower = prompt.lower()

        # If context is provided (from RAG, Vision or Web Search)
        if context and len(context) > 0:
            joined_context = " ".join(context)
            if any(img in prompt_lower for img in ["p&id", "pid", "diagram", "drawing", "schematic"]) and any(doc in prompt_lower for doc in ["document", "pdf", "spec", "report", "compare"]):
                return f"Cross-modal comparison: The valve specification in the PDF matches the 150# rating and tag FV-102 indicated on the P&ID drawing. Context: {joined_context}"
            elif any(img in prompt_lower for img in ["p&id", "pid", "diagram", "drawing", "schematic", "image", "blueprint"]):
                return f"Based on the P&ID diagram: Centrifugal pump P-101A/B is shown with isolation gate valves and a check valve on the 4-inch discharge line. Context: {joined_context}"
            elif any(k in prompt_lower for k in ["calculate", "compute", "formula", "flow rate", "pressure drop", "mass balance", "heat duty"]):
                return f"Calculation result: Based on the parameters in the document, the pressure drop across the pipe is calculated as 4.2 psi (28.9 kPa). Context: {joined_context}"
            elif "summarize" in prompt_lower or "summary" in prompt_lower:
                return f"Summary based on provided documents: {joined_context}"
            elif "compare" in prompt_lower:
                return f"Comparison based on provided documents: {joined_context}"
            elif any(k in prompt_lower for k in ["latest", "current", "news", "recent", "today", "web"]):
                return f"Based on web search results: {joined_context}"
            else:
                return f"Based on the provided documents: {joined_context}"

        # Direct queries without context
        if any(k in prompt_lower for k in ["calculate", "compute", "formula", "flow rate", "pressure drop", "mass balance", "math", "equation"]):
            return "Calculation result: Based on standard fluid dynamics principles, the estimated pressure drop is 4.2 psi (28.9 kPa)."
        elif any(img in prompt_lower for img in ["p&id", "pid", "diagram", "drawing", "schematic", "blueprint"]):
            return "Visual analysis: The P&ID diagram illustrates an automated control loop with sensor TT-101 and control valve TV-101."
        elif "python" in prompt_lower:
            return "Python is a high-level, general-purpose programming language known for its readable syntax and broad ecosystem."
        elif "artificial intelligence" in prompt_lower or "ai" in prompt_lower.split():
            return "Artificial Intelligence is a field of computer science dedicated to building systems capable of performing tasks that typically require human intelligence."
        elif "quantum" in prompt_lower:
            return "Quantum computing is a multidisciplinary field comprising aspects of computer science, physics, and mathematics that utilizes quantum mechanics to solve complex problems."
        else:
            return f"Synthesized answer for '{prompt.strip()}': This is a response based on general knowledge."



class MockWebSearchAgent(BaseWebSearchAgent):
    """
    Mock Web Search Agent simulating external search results.
    """

    async def search(self, query: str, num_results: int = 3) -> List[str]:
        return [
            f"Latest update for '{query}': Recent advancements demonstrate accelerated sovereign AI infrastructure deployments globally."
        ]

