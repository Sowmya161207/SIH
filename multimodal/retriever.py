"""Multimodal Evidence Retrieval and Context Assembler for MRPL Workbench."""

from typing import List, Dict, Any, Optional
from knowledge.retriever import search_documents
from .processor import MultimodalDocumentProcessor
from .schemas import PageImageMetadata, MultimodalContext


class MultimodalRetriever:
    """Retrieves both text chunks and associated page image/diagram metadata."""

    def __init__(self, processor: Optional[MultimodalDocumentProcessor] = None):
        self.processor = processor or MultimodalDocumentProcessor()

    def retrieve_multimodal_context(
        self,
        query: str,
        equipment_tag: Optional[str] = None,
        top_k_text: int = 3,
        top_k_images: int = 2
    ) -> MultimodalContext:
        """
        Assemble multimodal context containing text citations and page image metadata.
        """
        # 1. Search text chunks from knowledge base
        filter_dict = {"equipment_tag": equipment_tag} if equipment_tag else None
        search_res = search_documents(query, filters=filter_dict, top_k=top_k_text)
        text_evidence = [c.to_dict() for c in search_res.citations]

        # 2. Retrieve associated page images and diagrams
        matched_images: List[PageImageMetadata] = []
        target_tags = [equipment_tag.lower()] if equipment_tag else []

        for doc in self.processor._document_registry.values():
            for page in doc.pages:
                page_tags = [t.lower() for t in page.associated_equipment_tags]
                if not target_tags or any(tt in page_tags for tt in target_tags):
                    matched_images.append(page)
                elif any(kw in (page.caption or "").lower() for kw in query.lower().split()):
                    matched_images.append(page)

        # Rank/limit page images
        selected_images = matched_images[:top_k_images]

        return MultimodalContext(
            query=query,
            text_evidence=text_evidence,
            page_images=selected_images,
            equipment_tags=[equipment_tag] if equipment_tag else []
        )


_global_multimodal_retriever = MultimodalRetriever()


def retrieve_multimodal_context(
    query: str,
    equipment_tag: Optional[str] = None,
    top_k_text: int = 3,
    top_k_images: int = 2
) -> MultimodalContext:
    """Public helper function for multimodal context retrieval."""
    return _global_multimodal_retriever.retrieve_multimodal_context(
        query=query,
        equipment_tag=equipment_tag,
        top_k_text=top_k_text,
        top_k_images=top_k_images
    )
