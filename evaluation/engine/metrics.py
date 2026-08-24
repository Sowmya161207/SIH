"""
Evaluation Metrics & Statistical Calculation Module for Industrial RAG Benchmark.
Measures Retrieval Success, Source Correctness, Fact/Answer Correctness,
Citation Coverage, and categorizes failure cases.
"""

from typing import List, Dict, Any, Set
import re


class EvaluationMetrics:
    """Calculates granular evaluation metrics across industrial query evaluations."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Lowercases and cleans text for robust substring and fuzzy matching."""
        if not text:
            return ""
        # Normalize whitespace and hyphens
        text = text.lower()
        text = re.sub(r"[–—]", "-", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def evaluate_retrieval(
        retrieved_chunks: List[Dict[str, Any]], expected_sources: List[str], expected_pages: List[int]
    ) -> Dict[str, Any]:
        """
        Evaluates retrieval quality against expected source documents and pages.
        """
        retrieved_docs: Set[str] = {c["doc_name"] for c in retrieved_chunks}
        retrieved_pages: Set[int] = {c["page"] for c in retrieved_chunks}

        expected_docs_set = set(expected_sources)
        matched_docs = retrieved_docs.intersection(expected_docs_set)

        # Retrieval success: at least one expected document retrieved
        retrieval_success = len(matched_docs) > 0

        # Full source correctness: ALL expected documents retrieved
        source_correctness = (matched_docs == expected_docs_set)

        # Page match: at least one expected page retrieved
        page_matched = len(retrieved_pages.intersection(set(expected_pages))) > 0

        # Source Precision & Recall
        source_precision = len(matched_docs) / max(1, len(retrieved_docs))
        source_recall = len(matched_docs) / max(1, len(expected_docs_set))

        return {
            "retrieval_success": retrieval_success,
            "source_correctness": source_correctness,
            "page_matched": page_matched,
            "matched_sources": list(matched_docs),
            "missing_sources": list(expected_docs_set - matched_docs),
            "source_precision": round(source_precision, 3),
            "source_recall": round(source_recall, 3),
        }

    @staticmethod
    def evaluate_answer_facts(
        generated_or_context_text: str, expected_key_facts: List[str]
    ) -> Dict[str, Any]:
        """
        Measures coverage of expected key industrial facts in the retrieved context / answer.
        """
        norm_text = EvaluationMetrics.normalize_text(generated_or_context_text)
        matched_facts = []
        missing_facts = []

        for fact in expected_key_facts:
            norm_fact = EvaluationMetrics.normalize_text(fact)
            # Check direct inclusion or token overlap
            if norm_fact in norm_text:
                matched_facts.append(fact)
            else:
                # Sub-token overlap check for long procedural sentences
                fact_tokens = [t for t in re.split(r"[\s,–—\-]+", norm_fact) if len(t) > 2]
                if fact_tokens and sum(1 for t in fact_tokens if t in norm_text) / len(fact_tokens) >= 0.75:
                    matched_facts.append(fact)
                else:
                    missing_facts.append(fact)

        fact_coverage = len(matched_facts) / max(1, len(expected_key_facts))
        is_acceptable = fact_coverage >= 0.70  # Standard industrial threshold

        return {
            "is_acceptable": is_acceptable,
            "fact_coverage": round(fact_coverage, 3),
            "matched_facts": matched_facts,
            "missing_facts": missing_facts,
        }

    @staticmethod
    def classify_failure(
        retrieval_res: Dict[str, Any], fact_res: Dict[str, Any], is_multimodal: bool = False
    ) -> Optional[str]:
        """
        Classifies the exact failure mode for diagnostic reporting.
        """
        if not retrieval_res["retrieval_success"]:
            return "RETRIEVAL_MISS"
        if not retrieval_res["source_correctness"]:
            return "PARTIAL_SOURCE_RETRIEVAL"
        if not retrieval_res["page_matched"]:
            return "PAGE_MISALIGNMENT"
        if not fact_res["is_acceptable"]:
            if is_multimodal:
                return "CROSS_MODAL_DISCONNECT"
            return "KEY_FACT_OMISSION"
        return None
