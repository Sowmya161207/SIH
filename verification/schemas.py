"""Schemas and data structures for Claim Verification Layer.

Designed for Sovereign On-Premise Agentic AI Workbench (MRPL - SIH26117).
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Union


class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    INFERRED = "INFERRED"
    UNSUPPORTED = "UNSUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

    def __str__(self) -> str:
        return self.value


class ClaimModality(str, Enum):
    DEFINITE = "DEFINITE"          # "is broken", "exceeded limit", "failed"
    PROBABILISTIC = "PROBABILISTIC" # "possible", "likely", "suspected", "potential", "may indicate"
    RECOMMENDATION = "RECOMMENDATION" # "recommend", "should replace", "requires inspection"

    def __str__(self) -> str:
        return self.value


@dataclass
class EvidenceItem:
    text: str
    source_type: str = "general"   # "RAG", "Sensor", "Manual", "Lab", "Maintenance"
    source_id: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_input(cls, raw: Union[str, Dict[str, Any], "EvidenceItem"]) -> "EvidenceItem":
        if isinstance(raw, cls):
            return raw
        if isinstance(raw, str):
            return cls(text=raw.strip())
        if isinstance(raw, dict):
            return cls(
                text=raw.get("text") or raw.get("content") or raw.get("snippet") or str(raw),
                source_type=raw.get("source_type") or raw.get("source") or "general",
                source_id=raw.get("source_id") or raw.get("id"),
                confidence=float(raw.get("confidence", 1.0)),
                metadata=raw.get("metadata", {})
            )
        return cls(text=str(raw))


@dataclass
class Claim:
    text: str
    modality: ClaimModality = ClaimModality.DEFINITE
    keywords: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    source_finding: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["modality"] = str(self.modality)
        return data


@dataclass
class ClaimVerificationResult:
    claim: str
    status: Union[VerificationStatus, str]
    confidence: float
    supporting_evidence: List[str] = field(default_factory=list)
    reason: str = ""
    limitations: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "status": str(self.status),
            "confidence": round(self.confidence, 2),
            "supporting_evidence": self.supporting_evidence,
            "reason": self.reason,
            "limitations": self.limitations,
        }


@dataclass
class VerificationReport:
    results: List[ClaimVerificationResult]
    summary: Dict[str, int] = field(default_factory=dict)
    overall_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "overall_confidence": round(self.overall_confidence, 2),
            "results": [r.to_dict() for r in self.results],
        }
