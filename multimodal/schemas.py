"""Data schemas for Multimodal Industrial Document Understanding.

Designed for Sovereign On-Premise AI Workbench (MRPL - SIH26117).
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Union


class DiagramType(str, Enum):
    PID = "PID"                                 # Piping & Instrumentation Diagram
    MECHANICAL_DRAWING = "MECHANICAL_DRAWING"   # Cross-section assembly, dimensional drawing
    PERFORMANCE_CURVE = "PERFORMANCE_CURVE"     # Head-capacity, NPSH, efficiency curve
    ELECTRICAL_SCHEMATIC = "ELECTRICAL_SCHEMATIC" # Single-line diagram, wiring
    GENERAL_DIAGRAM = "GENERAL_DIAGRAM"         # Process flow diagram (PFD), block diagram
    TEXT_PAGE = "TEXT_PAGE"                     # Text-only or table page

    def __str__(self) -> str:
        return self.value


@dataclass
class PageImageMetadata:
    document_id: str
    page_number: int
    image_id: str
    image_filename: str
    image_path: str
    width: int = 1920
    height: int = 1080
    mime_type: str = "image/png"
    has_diagram: bool = False
    diagram_type: Optional[Union[DiagramType, str]] = None
    caption: Optional[str] = None
    extracted_text: Optional[str] = None
    associated_equipment_tags: List[str] = field(default_factory=list)
    associated_chunk_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.diagram_type:
            d["diagram_type"] = str(self.diagram_type)
        return d


@dataclass
class ExtractedDocument:
    document_id: str
    filename: str
    total_pages: int
    pages: List[PageImageMetadata] = field(default_factory=list)
    text_chunks: List[Dict[str, Any]] = field(default_factory=list)
    created_at: Optional[str] = None
    storage_directory: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "total_pages": self.total_pages,
            "created_at": self.created_at,
            "storage_directory": self.storage_directory,
            "pages": [p.to_dict() for p in self.pages],
            "text_chunks": self.text_chunks,
        }


@dataclass
class MultimodalContext:
    query: str
    text_evidence: List[Dict[str, Any]] = field(default_factory=list)
    page_images: List[PageImageMetadata] = field(default_factory=list)
    equipment_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "equipment_tags": self.equipment_tags,
            "text_evidence": self.text_evidence,
            "page_images": [p.to_dict() for p in self.page_images],
        }
