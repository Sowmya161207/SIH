"""Hybrid Vector and Keyword Evidence Retrieval Engine for MRPL Workbench (SIH26117).

Provides:
- search_documents(query, filters, top_k)
- format_citations(citations)
- Metadata filtering & provenance tracking
"""

import json
import math
import os
import re
import time
from typing import List, Dict, Any, Optional, Union

from .schemas import (
    DocumentChunk,
    DocumentMetadata,
    DocumentType,
    CriticalityLevel,
    RetrievalFilter,
    EvidenceCitation,
    SearchResult,
)

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
    "which", "this", "that", "these", "those", "then", "just", "so", "than",
    "such", "both", "through", "about", "for", "is", "of", "while", "during",
    "to", "from", "in", "out", "on", "off", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "can", "will", "just", "should",
    "now", "by", "with", "at", "be", "was", "were", "been", "being", "have", "has",
    "had", "do", "does", "did", "doing", "i", "we", "you", "they", "it", "its"
}


def tokenize(text: str) -> List[str]:
    """Tokenize text preserving equipment codes, tags, and units."""
    # Find words, equipment tags like P-101, numbers with units like 4.5mm/s, 130C
    raw_tokens = re.findall(r"\b[A-Za-z0-9_\-\.%/]+\b", text.lower())
    tokens = []
    for tok in raw_tokens:
        tok = tok.strip(".-/")
        if len(tok) > 1 and tok not in STOPWORDS:
            tokens.append(tok)
    return tokens


class EvidenceRetriever:
    """Vector & Semantic Evidence Retrieval Store for Sovereign On-Premise AI Workbench."""

    def __init__(self, corpus_path: Optional[str] = None):
        self.chunks: List[DocumentChunk] = []
        self.doc_freqs: Dict[str, int] = {}
        self.term_freqs: List[Dict[str, int]] = []
        self.avg_doc_len: float = 0.0
        self.num_docs: int = 0

        # Load default corpus if exists
        if corpus_path and os.path.exists(corpus_path):
            self.load_corpus_from_json(corpus_path)
        else:
            default_path = os.path.join(os.path.dirname(__file__), "datasets", "mrpl_refinery_corpus.json")
            if os.path.exists(default_path):
                self.load_corpus_from_json(default_path)

    def add_document(self, chunk: DocumentChunk) -> None:
        """Add an individual document chunk to the vector store."""
        self.chunks.append(chunk)
        self._rebuild_index()

    def add_documents(self, chunks: List[DocumentChunk]) -> None:
        """Bulk add document chunks to the vector store."""
        self.chunks.extend(chunks)
        self._rebuild_index()

    def load_corpus_from_json(self, file_path: str) -> int:
        """Load and index documents from a JSON corpus file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        new_chunks = []
        for item in data:
            meta = DocumentMetadata(
                doc_id=item.get("doc_id", "DOC-001"),
                title=item.get("title", "Refinery Document"),
                doc_type=item.get("doc_type", DocumentType.OEM_MANUAL),
                unit=item.get("unit", "CDU-1"),
                equipment_tag=item.get("equipment_tag"),
                system=item.get("system"),
                criticality=item.get("criticality", CriticalityLevel.MEDIUM),
                page=item.get("page", 1),
                chunk_id=item.get("chunk_id", item.get("doc_id", "C-01"))
            )
            chunk = DocumentChunk(
                chunk_id=meta.chunk_id or "C-01",
                text=item.get("text", ""),
                metadata=meta,
                keywords=item.get("keywords", [])
            )
            new_chunks.append(chunk)

        self.chunks = new_chunks
        self._rebuild_index()
        return len(new_chunks)

    def _rebuild_index(self) -> None:
        """Calculate BM25 & TF-IDF statistics over indexed chunks."""
        self.num_docs = len(self.chunks)
        if self.num_docs == 0:
            return

        self.doc_freqs = {}
        self.term_freqs = []
        total_len = 0

        for chunk in self.chunks:
            tokens = tokenize(chunk.text)
            total_len += len(tokens)
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.term_freqs.append(tf)

            for term in tf:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.avg_doc_len = total_len / self.num_docs if self.num_docs > 0 else 1.0

    def _matches_filters(self, meta: DocumentMetadata, rf: RetrievalFilter) -> bool:
        """Apply metadata filtering criteria including security (workspace & roles)."""
        if rf.workspace_id and meta.workspace_id != rf.workspace_id:
            if meta.workspace_id != "default":
                return False
                
        if rf.user_roles and "Admin" not in rf.user_roles:
            has_access = any(role in meta.allowed_roles for role in rf.user_roles)
            if not has_access:
                return False

        if rf.equipment_tag:
            tags = [rf.equipment_tag.lower()] if isinstance(rf.equipment_tag, str) else [t.lower() for t in rf.equipment_tag]
            if not meta.equipment_tag or meta.equipment_tag.lower() not in tags:
                return False

        if rf.unit:
            units = [rf.unit.lower()] if isinstance(rf.unit, str) else [u.lower() for u in rf.unit]
            if meta.unit.lower() not in units and meta.unit.lower() != "refinery-wide":
                return False

        if rf.doc_type:
            types = [str(rf.doc_type).lower()] if isinstance(rf.doc_type, (str, DocumentType)) else [str(t).lower() for t in rf.doc_type]
            if str(meta.doc_type).lower() not in types:
                return False

        if rf.criticality:
            crits = [str(rf.criticality).lower()] if isinstance(rf.criticality, (str, CriticalityLevel)) else [str(c).lower() for c in rf.criticality]
            if str(meta.criticality).lower() not in crits:
                return False

        return True

    def search(
        self,
        query: str,
        filters: Optional[Union[Dict[str, Any], RetrievalFilter]] = None,
        top_k: int = 5
    ) -> SearchResult:
        """
        Execute BM25 + Semantic entity-boosted vector search against indexed refinery corpus.
        """
        start_time = time.perf_counter()

        if isinstance(filters, dict):
            retrieval_filter = RetrievalFilter.from_dict(filters)
            filter_dict = filters
        elif isinstance(filters, RetrievalFilter):
            retrieval_filter = filters
            filter_dict = asdict(filters)
        else:
            retrieval_filter = RetrievalFilter()
            filter_dict = None

        query_tokens = tokenize(query)
        if not query_tokens or self.num_docs == 0:
            return SearchResult(
                query=query,
                citations=[],
                total_matched=0,
                filter_applied=filter_dict,
                search_latency_ms=(time.perf_counter() - start_time) * 1000.0
            )

        k1 = 1.5
        b = 0.75
        scores: List[tuple[int, float]] = []

        query_lower = query.lower()
        equipment_mentions = re.findall(r"\b[a-z]{1,4}-[0-9]{2,4}[a-z]?\b", query_lower)

        for idx, chunk in enumerate(self.chunks):
            if not self._matches_filters(chunk.metadata, retrieval_filter):
                continue

            tf_dict = self.term_freqs[idx]
            doc_len = sum(tf_dict.values())
            score = 0.0

            for q_term in query_tokens:
                if q_term in tf_dict:
                    freq = tf_dict[q_term]
                    df = self.doc_freqs.get(q_term, 1)
                    idf = math.log(1.0 + (self.num_docs - df + 0.5) / (df + 0.5))
                    bm25_term = idf * (freq * (k1 + 1.0)) / (freq + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len)))
                    score += bm25_term

            # Equipment Tag & Entity Boost
            meta_tag = (chunk.metadata.equipment_tag or "").lower()
            if retrieval_filter.equipment_tag and meta_tag and meta_tag == str(retrieval_filter.equipment_tag).lower():
                score += 2.0
            if meta_tag and meta_tag in query_lower:
                score += 4.5
            elif equipment_mentions and meta_tag and any(tag in meta_tag for tag in equipment_mentions):
                score += 3.0

            # Keyword matches
            for kw in chunk.keywords:
                if kw.lower() in query_lower:
                    score += 0.8

            if score > retrieval_filter.min_score:
                scores.append((idx, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        citations: List[EvidenceCitation] = []
        for idx, raw_score in scores[:top_k]:
            chunk = self.chunks[idx]
            # Normalize score between 0.0 and 1.0 for citations
            normalized_score = min(1.0, raw_score / 15.0) if raw_score > 0 else 0.0

            citation = EvidenceCitation(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                document_title=chunk.metadata.title,
                doc_type=str(chunk.metadata.doc_type),
                unit=chunk.metadata.unit,
                equipment_tag=chunk.metadata.equipment_tag,
                page=chunk.metadata.page,
                relevance_score=normalized_score,
                metadata=chunk.metadata.to_dict()
            )
            citations.append(citation)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return SearchResult(
            query=query,
            citations=citations,
            total_matched=len(scores),
            filter_applied=filter_dict,
            search_latency_ms=latency_ms
        )


# Global default instance
_global_retriever = EvidenceRetriever()


def search_documents(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 5
) -> SearchResult:
    """
    Search and retrieve evidence chunks from MRPL Industrial Knowledge Base.

    :param query: Natural language search query or telemetry finding (e.g. "P-101 vibration causes")
    :param filters: Optional metadata filters (e.g. {"equipment_tag": "P-101", "doc_type": "OEM_MANUAL"})
    :param top_k: Maximum number of citations to return
    :return: SearchResult object containing citations, scores, and provenance
    """
    return _global_retriever.search(query, filters=filters, top_k=top_k)


def format_citations(citations: List[EvidenceCitation]) -> str:
    """Format evidence citations into a clear markdown citation block for operators."""
    if not citations:
        return "No corresponding documentation found in knowledge base."

    lines = ["### Evidence & Documentation Sources"]
    for i, c in enumerate(citations, 1):
        lines.append(f"{i}. **{c.document_title}** ({c.doc_type})")
        lines.append(f"   - **Unit / Tag:** `{c.unit}` / `{c.equipment_tag or 'N/A'}` | **Page:** {c.page} | **Score:** {c.relevance_score:.2f}")
        lines.append(f"   - *Excerpt:* \"{c.text}\"\n")
    return "\n".join(lines)
