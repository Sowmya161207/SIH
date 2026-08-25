"""
evidence.py
-----------
Hallucination / Evidence Layer for Santhosh's Orchestrator.
Constructs verified evidence objects linking claims to retrieved source chunks & confidence scores.
"""

from typing import Dict, Any, List, Optional


def build_evidence(
    claim: str,
    retrieved_chunk: Dict[str, Any],
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Construct a standardized Evidence Object.

    Structure:
        {
            "claim": "...",
            "source_document": "...",
            "page": 1,
            "retrieved_text": "...",
            "confidence": 0.92
        }
    """
    source_doc = (
        retrieved_chunk.get("source")
        or retrieved_chunk.get("filename")
        or retrieved_chunk.get("document_id")
        or "unknown.pdf"
    )

    score = confidence if confidence is not None else retrieved_chunk.get("score", 0.0)

    return {
        "claim": claim,
        "source_document": source_doc,
        "page": retrieved_chunk.get("page", 1),
        "retrieved_text": retrieved_chunk.get("content") or retrieved_chunk.get("text", ""),
        "confidence": float(round(score, 4)),
    }


def attach_evidence_to_response(
    claims: List[str],
    retrieved_chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Attach evidence objects for a list of claims against retrieved chunks.
    """
    evidence_list = []
    for i, claim in enumerate(claims):
        chunk = retrieved_chunks[i] if i < len(retrieved_chunks) else (retrieved_chunks[0] if retrieved_chunks else {})
        if chunk:
            evidence_list.append(build_evidence(claim, chunk))
    return evidence_list
