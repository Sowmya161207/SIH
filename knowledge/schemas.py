"""Schemas for Knowledge Base, Metadata Organization, and Evidence Retrieval.

MRPL Sovereign On-Premise AI Workbench (SIH26117).
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Union


class DocumentType(str, Enum):
    OEM_MANUAL = "OEM_MANUAL"
    SOP = "SOP"
    MAINTENANCE_LOG = "MAINTENANCE_LOG"
    INCIDENT_REPORT = "INCIDENT_REPORT"
    ALARM_SPEC = "ALARM_SPEC"
    PID_SPEC = "PID_SPEC"

    def __str__(self) -> str:
        return self.value


class CriticalityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value


@dataclass
class DocumentMetadata:
    doc_id: str
    title: str
    doc_type: Union[DocumentType, str]
    unit: str                         # e.g., "CDU-1", "VGO-HT", "FCCU", "Utilities"
    equipment_tag: Optional[str] = None # e.g., "P-101", "K-101", "P-204"
    system: Optional[str] = None      # e.g., "Crude Feed Pump System", "Lube Oil System"
    criticality: Union[CriticalityLevel, str] = CriticalityLevel.MEDIUM
    page: Optional[int] = 1
    chunk_id: Optional[str] = None
    created_date: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["doc_type"] = str(self.doc_type)
        d["criticality"] = str(self.criticality)
        return d


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: DocumentMetadata
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": self.metadata.to_dict(),
            "keywords": self.keywords,
        }


@dataclass
class RetrievalFilter:
    equipment_tag: Optional[Union[str, List[str]]] = None
    unit: Optional[Union[str, List[str]]] = None
    doc_type: Optional[Union[DocumentType, str, List[str]]] = None
    criticality: Optional[Union[CriticalityLevel, str, List[str]]] = None
    min_score: float = 0.0

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "RetrievalFilter":
        if not d:
            return cls()
        return cls(
            equipment_tag=d.get("equipment_tag") or d.get("equipment") or d.get("tag"),
            unit=d.get("unit"),
            doc_type=d.get("doc_type") or d.get("type"),
            criticality=d.get("criticality") or d.get("severity"),
            min_score=float(d.get("min_score", 0.0))
        )


@dataclass
class EvidenceCitation:
    chunk_id: str
    text: str
    document_title: str
    doc_type: str
    unit: str
    equipment_tag: Optional[str]
    page: Optional[int]
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "document_title": self.document_title,
            "doc_type": self.doc_type,
            "unit": self.unit,
            "equipment_tag": self.equipment_tag,
            "page": self.page,
            "relevance_score": round(self.relevance_score, 4),
            "metadata": self.metadata,
        }

    def format_citation_string(self) -> str:
        tag_info = f" [{self.equipment_tag}]" if self.equipment_tag else ""
        page_info = f", p.{self.page}" if self.page else ""
        return f"[{self.doc_type}] {self.document_title}{tag_info} ({self.unit}{page_info}) - Score: {self.relevance_score:.2f}"


@dataclass
class SearchResult:
    query: str
    citations: List[EvidenceCitation]
    total_matched: int
    filter_applied: Optional[Dict[str, Any]] = None
    search_latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "total_matched": self.total_matched,
            "search_latency_ms": round(self.search_latency_ms, 2),
            "filter_applied": self.filter_applied,
            "citations": [c.to_dict() for c in self.citations],
        }

    def get_evidence_texts(self) -> List[str]:
        return [c.text for c in self.citations]
