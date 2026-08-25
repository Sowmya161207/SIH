"""
Real adapters connecting the Planner/Orchestrator to the existing
Sovereign AI Workbench backend services.

The Planner works only with abstract interfaces.
These adapters translate the real SIH service outputs into the
Planner's standardized contracts.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .interfaces import (
    BaseRAGAgent,
    BaseAnalyticsAgent,
    BaseLLMAgent,
    BaseEvidenceVerifier,
)

from .schemas import (
    RAGResult,
    RAGChunk,
    SourceMetadata,
    EvidenceItem,
    VerificationResult,
)


class RealRAGAgent(BaseRAGAgent):
    """Adapter for the existing backend RAG retrieval service."""

    async def search_documents(
        self,
        query: str,
        user_role: Optional[str] = None,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> RAGResult:

        from backend.app.services.rag_service import retrieve

        results = retrieve(
            query=query,
            document_ids=document_ids,
            user_role=user_role,
            top_k=top_k,
        )

        chunks: List[RAGChunk] = []
        sources: List[SourceMetadata] = []

        for index, item in enumerate(results):

            source = SourceMetadata(
                document=item.get("source", "unknown.pdf"),
                page=item.get("page"),
                chunk_id=item.get(
                    "chunk_id",
                    f"retrieved_{index}",
                ),
                score=float(item.get("score", 0.0)),
            )

            chunk = RAGChunk(
                text=item.get(
                    "content",
                    item.get("text", ""),
                ),
                source=source,
            )

            chunks.append(chunk)

            if not any(
                s.document == source.document
                and s.page == source.page
                for s in sources
            ):
                sources.append(source)

        return RAGResult(
            chunks=chunks,
            sources=sources,
        )


class RealAnalyticsAgent(BaseAnalyticsAgent):
    """
    Adapter for the existing analytics module.

    Uses the project's Pump P-101 telemetry CSV by default.
    """

    def __init__(
        self,
        data_path: Optional[str] = None,
    ):
        if data_path:
            self.data_path = Path(data_path)
        else:
            project_root = Path(__file__).resolve().parents[1]
            self.data_path = (
                project_root
                / "data"
                / "raw"
                / "pump_p101_sensor_data.csv"
            )

    async def get_maintenance_analytics(
        self,
        equipment_id: Optional[str] = None,
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        from analytics.main import analyze_sensor_data

        if not self.data_path.exists():
            return {
                "equipment_id": equipment_id or "P-101",
                "telemetry_available": False,
                "anomaly_detected": False,
                "confidence": 0.0,
                "error": (
                    f"Telemetry file not found: "
                    f"{self.data_path}"
                ),
            }

        try:
            results = analyze_sensor_data(
                self.data_path
            )

            equipment = results.get(
                "equipment",
                equipment_id or "P-101",
            )

            anomalies = results.get(
                "anomalies",
                {},
            )

            risk_level = results.get(
                "risk_level",
                "unknown",
            )

            return {
                "equipment_id": equipment_id or equipment,
                "telemetry_available": True,

                "health_score": results.get(
                    "health_score"
                ),

                "risk_level": risk_level,

                "risk_description": results.get(
                    "risk_description"
                ),

                "health_breakdown": results.get(
                    "health_breakdown",
                    {},
                ),

                "anomalies": anomalies,

                "trends": results.get(
                    "trends",
                    {},
                ),

                "chart_data": results.get(
                    "chart_data",
                    [],
                ),

                "anomaly_detected": (
                    anomalies.get(
                        "total_critical_breaches",
                        0,
                    ) > 0
                    or anomalies.get(
                        "total_warning_breaches",
                        0,
                    ) > 0
                    or anomalies.get(
                        "total_statistical_outliers",
                        0,
                    ) > 0
                ),

                "recommended_action": (
                    "Immediate maintenance investigation recommended."
                    if risk_level in (
                        "critical",
                        "high",
                    )
                    else "Continue monitoring equipment condition."
                ),

                "confidence": 0.95,
            }

        except Exception as exc:
            return {
                "equipment_id": equipment_id or "P-101",
                "telemetry_available": False,
                "anomaly_detected": False,
                "confidence": 0.0,
                "error": str(exc),
            }


class RealLLMAgent(BaseLLMAgent):
    """
    Adapter for the existing local Ollama LLM service.
    """

    async def generate(
        self,
        prompt: str,
        context: Optional[List[str]] = None,
        system_instruction: Optional[str] = None,
    ) -> str:

        from backend.app.services.llm_service import (
            generate_answer,
        )

        evidence: List[Dict[str, Any]] = []

        for index, item in enumerate(
            context or []
        ):
            evidence.append(
                {
                    "source": "orchestrator_context",
                    "page": None,
                    "title": f"context_{index + 1}",
                    "text": item,
                }
            )

        # If there is no evidence, the existing LLM service
        # intentionally refuses to answer.
        if not evidence:
            return (
                "No supporting evidence was available "
                "for this request."
            )

        return await generate_answer(
            question=prompt,
            evidence=evidence,
        )


class RealEvidenceVerifier(BaseEvidenceVerifier):
    """
    Lightweight deterministic evidence verifier.

    This is intentionally separate from the LLM so the basic
    hallucination guard does not depend on another model call.
    """

    async def verify_evidence(
        self,
        query: str,
        evidence: List[EvidenceItem],
        answer: Optional[str] = None,
    ) -> VerificationResult:

        if not evidence:
            return VerificationResult(
                is_sufficient=False,
                confidence=0.0,
                reason=(
                    "No supporting evidence was retrieved "
                    "from the available knowledge sources."
                ),
                verified_evidence=[],
            )

        valid_evidence = [
            item
            for item in evidence
            if item.content
            and item.content.strip()
            and 0.0 <= item.confidence <= 1.0
        ]

        if not valid_evidence:
            return VerificationResult(
                is_sufficient=False,
                confidence=0.0,
                reason=(
                    "Retrieved evidence was empty or "
                    "contained invalid confidence values."
                ),
                verified_evidence=[],
            )

        average_confidence = (
            sum(
                item.confidence
                for item in valid_evidence
            )
            / len(valid_evidence)
        )

        sufficient = average_confidence >= 0.40

        return VerificationResult(
            is_sufficient=sufficient,
            confidence=round(
                average_confidence,
                2,
            ),
            reason=(
                "Evidence passed deterministic "
                "grounding checks."
                if sufficient
                else
                "Evidence confidence is below "
                "the required threshold."
            ),
            verified_evidence=valid_evidence,
        )