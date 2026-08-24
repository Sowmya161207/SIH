"""
Concrete adapters and mock implementations of the agent interfaces.
Provides ready-to-run mocks for testing/demos as well as pluggable HTTP adapters.
"""

import json
import re
from typing import List, Optional, Dict, Any
from .interfaces import (
    BasePlannerLLMClient,
    BaseRAGAgent,
    BaseVisionAgent,
    BaseAnalyticsAgent,
    BaseEvidenceVerifier,
    BaseLLMAgent,
    BaseWebSearchAgent
)
from .schemas import RAGResult, RAGChunk, SourceMetadata, EvidenceItem, VerificationResult


class MockPlannerLLMClient(BasePlannerLLMClient):
    """
    Deterministic rule-based planning LLM mock for unit testing and offline demo execution.
    Decomposes user queries into atomic steps across RAG, Vision, Analytics, Verification, and LLM synthesis.
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

        # 1. Ambiguous / underspecified / unsupported queries
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
        # 2. Complex Incident Investigation (e.g. Pump P-101 failure investigation with root-cause & maintenance)
        elif ("investigate" in lower_query or "root cause" in lower_query or "why" in lower_query) and \
             ("fail" in lower_query or "tripped" in lower_query or "breakdown" in lower_query or "incident" in lower_query) and \
             ("pump" in lower_query or "p-101" in lower_query or "equipment" in lower_query or "compressor" in lower_query or "valve" in lower_query):
            plan_dict = {
                "intent": "incident_investigation",
                "requires_rag": True,
                "requires_web": False,
                "steps": [
                    {
                        "step": 1,
                        "tool": "rag",
                        "action": "retrieve",
                        "input": f"{clean_query} - incident report and alarm logs"
                    },
                    {
                        "step": 2,
                        "tool": "rag",
                        "action": "retrieve",
                        "input": f"{clean_query} - maintenance history and inspection logs"
                    },
                    {
                        "step": 3,
                        "tool": "rag",
                        "action": "retrieve",
                        "input": f"{clean_query} - equipment operating manual and limits"
                    },
                    {
                        "step": 4,
                        "tool": "analytics",
                        "action": "analytics",
                        "input": "P-101 telemetry vibration, temperature, and pressure anomaly analysis"
                    },
                    {
                        "step": 5,
                        "tool": "verify",
                        "action": "verify",
                        "input": "Verify evidence grounding across incident logs, manuals, and sensor telemetry."
                    },
                    {
                        "step": 6,
                        "tool": "llm",
                        "action": "synthesize",
                        "input": "Synthesize comprehensive root-cause failure analysis and required maintenance actions."
                    }
                ]
            }
        # 3. Maintenance Analytics Question (RAG + Telemetry Analytics)
        elif ("maintenance" in lower_query or "telemetry" in lower_query or "vibration" in lower_query or "bearing" in lower_query or "health" in lower_query) and \
             any(k in lower_query for k in ["p-101", "pump", "compressor", "c-200", "motor", "status", "schedule", "sensor"]):
            plan_dict = {
                "intent": "maintenance_analytics",
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
                        "tool": "analytics",
                        "action": "analytics",
                        "input": clean_query
                    },
                    {
                        "step": 3,
                        "tool": "verify",
                        "action": "verify",
                        "input": "Verify maintenance procedures and telemetry anomaly evidence."
                    },
                    {
                        "step": 4,
                        "tool": "llm",
                        "action": "synthesize",
                        "input": "Synthesize maintenance status, sensor condition, and actionable recommendations."
                    }
                ]
            }
        # 4. Multimodal QA (cross-referencing document text/specs AND P&ID/diagrams/images)
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
                        "tool": "vision",
                        "action": "analyze_image",
                        "input": clean_query
                    },
                    {
                        "step": 3,
                        "tool": "verify",
                        "action": "verify",
                        "input": "Verify cross-modal consistency between document specifications and visual diagram."
                    },
                    {
                        "step": 4,
                        "tool": "llm",
                        "action": "synthesize",
                        "input": "Synthesize cross-modal response combining document text and visual diagram annotations."
                    }
                ]
            }
        # 5. Image / P&ID QA (Visual inspection of diagrams, blueprints, piping & instrumentation drawings)
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
        # 6. Calculation / Quantitative Reasoning
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
        # 7. Document comparison
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
        # 8. Document summarization
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
        # 9. Document Q&A (uploaded / pdf / document / security mechanisms / policy / equipment / manual / spec / etc.)
        elif any(k in lower_query for k in ["pdf", "document", "uploaded", "file", "security mechanism", "policy", "report", "manual", "spec", "specification", "limit", "operating", "procedure", "datasheet", "standard", "equipment"]):
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

        # 10. Web Search
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
        # 11. General Knowledge QA
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
    Interacts via the clean search_documents(query, user_role, top_k, ...) contract.
    """

    def __init__(self, sample_document: str = "industrial_operations_manual.pdf", sample_page: int = 12):
        self.sample_document = sample_document
        self.sample_page = sample_page

    async def search_documents(
        self,
        query: str,
        user_role: Optional[str] = None,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        return await self.retrieve(query=query, document_ids=document_ids, filters=filters)

    async def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        query_lower = query.lower()

        # Simulated no-evidence case for testing hallucination guard
        if any(k in query_lower for k in ["nonexistent", "no_evidence", "unknown_equipment_xyz", "empty_kb"]):
            return RAGResult(chunks=[], sources=[])

        doc_name = (document_ids[0] if document_ids and len(document_ids) > 0 else self.sample_document)

        # Incident report query
        if "incident" in query_lower or "alarm" in query_lower:
            chunk1 = RAGChunk(
                text="Incident Report IR-2026-088: Pump P-101 experienced high vibration (8.2 mm/s) leading to mechanical seal blowout and automatic emergency shutdown at 04:12 UTC.",
                source=SourceMetadata(document="pump_p101_incident_report.pdf", page=1, chunk_id="ir_001", score=0.96)
            )
            chunk2 = RAGChunk(
                text="Post-trip inspection: Excessive axial shaft displacement observed; primary seal faces showed severe thermal cracking and dry-running wear.",
                source=SourceMetadata(document="pump_p101_incident_report.pdf", page=2, chunk_id="ir_002", score=0.92)
            )
            return RAGResult(chunks=[chunk1, chunk2], sources=[chunk1.source, chunk2.source])

        # Maintenance history query
        elif "maintenance" in query_lower or "history" in query_lower or "log" in query_lower:
            chunk1 = RAGChunk(
                text="Maintenance Log P-101: Last major seal overhaul was performed 18 months ago (recommended interval: 12 months). Routine lubrication was missed during the Q2 maintenance cycle.",
                source=SourceMetadata(document="pump_p101_maintenance_history.pdf", page=4, chunk_id="maint_001", score=0.94)
            )
            return RAGResult(chunks=[chunk1], sources=[chunk1.source])

        # Equipment manual query
        elif "manual" in query_lower or "specification" in query_lower or "operating" in query_lower:
            chunk1 = RAGChunk(
                text="Pump P-101 Technical Manual (Model ANSI-B73.1): Maximum allowable vibration is 4.5 mm/s RMS. Operating above 7.0 mm/s causes catastrophic seal face deflection. Seal flush plan 11 required.",
                source=SourceMetadata(document="pump_p101_technical_manual.pdf", page=15, chunk_id="man_001", score=0.91)
            )
            return RAGResult(chunks=[chunk1], sources=[chunk1.source])

        # Default document chunks
        chunk1 = RAGChunk(
            text="The Sovereign AI system implements zero-trust access control with hardware-backed encryption modules.",
            source=SourceMetadata(document=doc_name, page=self.sample_page, chunk_id="chunk_001", score=0.92)
        )
        chunk2 = RAGChunk(
            text="All data transfers within the enclave are authenticated using mTLS and verified against policy constraints.",
            source=SourceMetadata(document=doc_name, page=self.sample_page + 1, chunk_id="chunk_002", score=0.88)
        )
        return RAGResult(chunks=[chunk1, chunk2], sources=[chunk1.source, chunk2.source])



class MockVisionAgent(BaseVisionAgent):
    """
    Mock Vision / Multimodal Agent simulating P&ID diagram and blueprint inspection.
    """

    async def analyze_image(
        self,
        query: str,
        image_path: Optional[str] = None,
        image_data: Optional[Any] = None
    ) -> Dict[str, Any]:
        query_lower = query.lower()
        if "nonexistent" in query_lower or "empty" in query_lower:
            return {"detected_components": [], "description": "No visual components detected.", "confidence": 0.0}

        return {
            "image_id": image_path or "pid_diagram_drawing_01.svg",
            "detected_components": [
                {"tag": "P-101A", "type": "Centrifugal Pump", "status": "In-Service"},
                {"tag": "P-101B", "type": "Centrifugal Pump (Standby)", "status": "Standby"},
                {"tag": "CV-201", "type": "Check Valve", "line": "4-inch discharge"},
                {"tag": "FV-102", "type": "Flow Control Valve", "rating": "150# ANSI"}
            ],
            "description": "The P&ID diagram shows centrifugal pump P-101A/B with isolation gate valves, check valve CV-201 on the 4-inch discharge line, and flow control valve FV-102.",
            "confidence": 0.95
        }


class MockAnalyticsAgent(BaseAnalyticsAgent):
    """
    Mock Data Analytics Agent simulating real-time telemetry and maintenance analytics.
    """

    async def get_maintenance_analytics(
        self,
        equipment_id: Optional[str] = None,
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        query_lower = (query or "").lower()
        eq_id = equipment_id or ("P-101" if "p-101" in query_lower else "GENERIC-01")

        if "nonexistent" in query_lower:
            return {"equipment_id": eq_id, "telemetry_available": False, "anomaly_detected": False}

        return {
            "equipment_id": eq_id,
            "telemetry_available": True,
            "vibration_rms_mm_s": 7.8,
            "vibration_threshold_mm_s": 4.5,
            "bearing_temperature_c": 92.4,
            "bearing_temp_threshold_c": 80.0,
            "anomaly_detected": True,
            "health_index": "38% (Critical)",
            "failure_probability_48h": 0.89,
            "recommended_action": "Emergency maintenance required: Replace mechanical seal, inspect thrust bearing race, and restore lubrication plan 11.",
            "confidence": 0.96
        }


class MockEvidenceVerifier(BaseEvidenceVerifier):
    """
    Mock Evidence Verification Agent / Hallucination Guard.
    Validates that responses are grounded in verified evidence from RAG, Vision, and Analytics.
    """

    async def verify_evidence(
        self,
        query: str,
        evidence: List[EvidenceItem],
        answer: Optional[str] = None
    ) -> VerificationResult:
        if not evidence or len(evidence) == 0:
            return VerificationResult(
                is_sufficient=False,
                confidence=0.0,
                reason="Insufficient evidence: No relevant documents, telemetry, or visual diagrams were found in the knowledge repository.",
                verified_evidence=[]
            )

        # Calculate average confidence across collected evidence
        avg_conf = sum(item.confidence for item in evidence) / len(evidence)
        if avg_conf < 0.3:
            return VerificationResult(
                is_sufficient=False,
                confidence=avg_conf,
                reason="Evidence confidence below reliable threshold (< 0.3).",
                verified_evidence=evidence
            )

        return VerificationResult(
            is_sufficient=True,
            confidence=round(avg_conf, 2),
            reason="Evidence successfully verified across knowledge bases.",
            verified_evidence=evidence
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

        # If context is provided (from RAG, Vision, or Analytics)
        if context and len(context) > 0:
            joined_context = " ".join(context)
            if "investigate" in prompt_lower or "why" in prompt_lower or "failed" in prompt_lower or "incident" in prompt_lower:
                return (
                    "Root-Cause Failure & Maintenance Investigation:\n"
                    "1. Cause of Failure: Pump P-101 experienced high vibration (7.8 - 8.2 mm/s) exceeding the 4.5 mm/s manual limit, causing dry running and thermal blowout of the mechanical seal.\n"
                    "2. Maintenance History: The seal overhaul was overdue by 6 months, with missed Q2 lubrication.\n"
                    "3. Required Maintenance Actions: (a) Immediate replacement of primary seal faces (ANSI Plan 11); (b) Inspection and relubrication of thrust bearings; (c) Recalibrate vibration sensors prior to restart."
                )
            elif "maintenance" in prompt_lower or "telemetry" in prompt_lower or "analytics" in prompt_lower:
                return f"Maintenance Status & Recommendation: Telemetry indicates critical vibration (7.8 mm/s) and elevated bearing temperature (92.4°C). Recommended Action: Replace mechanical seal and restore lubrication. Context: {joined_context}"
            elif any(img in prompt_lower for img in ["p&id", "pid", "diagram", "drawing", "schematic"]) and any(doc in prompt_lower for doc in ["document", "pdf", "spec", "report", "compare"]):
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


