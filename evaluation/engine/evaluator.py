"""
Main RAG Evaluator for SIH PS 26117 Industrial Document Intelligence.
Runs automated benchmarks across the 25 industrial questions and computes
repeatable quantitative evaluation metrics.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from evaluation.dataset import load_industrial_test_set
from evaluation.engine.document_indexer import LocalDocumentIndexer
from evaluation.engine.metrics import EvaluationMetrics


class RAGEvaluator:
    """
    Automated evaluation framework for industrial RAG systems.
    Executes repeatable retrieval and fact verification benchmarks.
    """

    def __init__(self, indexer: Optional[LocalDocumentIndexer] = None):
        self.indexer = indexer or LocalDocumentIndexer()
        self.test_set = load_industrial_test_set()

    def evaluate_question(
        self, question_item: Dict[str, Any], top_k: int = 4
    ) -> Dict[str, Any]:
        """
        Evaluates a single question benchmark item.
        """
        q_id = question_item["id"]
        category = question_item["category"]
        question = question_item["question"]
        expected_sources = question_item["expected_source"]
        expected_pages = question_item.get("expected_pages", [])
        expected_key_facts = question_item.get("expected_key_facts", [])
        is_multimodal = question_item.get("is_multimodal", False)

        # 1. Retrieve chunks from indexer
        retrieved_chunks = self.indexer.search(question, top_k=top_k)

        # 2. Evaluate retrieval & source attribution
        retrieval_res = EvaluationMetrics.evaluate_retrieval(
            retrieved_chunks, expected_sources, expected_pages
        )

        # 3. Combine retrieved context to evaluate factual coverage
        combined_context = " ".join(c["text"] for c in retrieved_chunks)
        fact_res = EvaluationMetrics.evaluate_answer_facts(
            combined_context, expected_key_facts
        )

        # 4. Diagnose failure mode (if any)
        failure_type = EvaluationMetrics.classify_failure(
            retrieval_res, fact_res, is_multimodal=is_multimodal
        )

        return {
            "id": q_id,
            "category": category,
            "query_type": question_item.get("query_type", "lookup"),
            "question": question,
            "is_multimodal": is_multimodal,
            "expected_sources": expected_sources,
            "expected_pages": expected_pages,
            "retrieved_chunks": [
                {"doc_name": c["doc_name"], "page": c["page"], "score": c["score"]}
                for c in retrieved_chunks
            ],
            "retrieval_success": retrieval_res["retrieval_success"],
            "source_correctness": retrieval_res["source_correctness"],
            "page_matched": retrieval_res["page_matched"],
            "source_precision": retrieval_res["source_precision"],
            "source_recall": retrieval_res["source_recall"],
            "matched_sources": retrieval_res["matched_sources"],
            "missing_sources": retrieval_res["missing_sources"],
            "is_acceptable": fact_res["is_acceptable"],
            "fact_coverage": fact_res["fact_coverage"],
            "matched_facts": fact_res["matched_facts"],
            "missing_facts": fact_res["missing_facts"],
            "failure_type": failure_type,
        }

    def run_all(self, top_k: int = 4) -> Dict[str, Any]:
        """
        Executes the entire 25-question test suite and aggregates metrics.
        """
        questions = self.test_set.get("questions", [])
        detailed_results = []

        total_questions = len(questions)
        retrieved_relevant_count = 0
        correct_source_count = 0
        answer_acceptable_count = 0
        multimodal_total = 0
        multimodal_successful = 0

        category_breakdown: Dict[str, Dict[str, int]] = {}
        failure_cases: List[Dict[str, Any]] = []

        for q in questions:
            res = self.evaluate_question(q, top_k=top_k)
            detailed_results.append(res)

            cat = res["category"]
            if cat not in category_breakdown:
                category_breakdown[cat] = {
                    "total": 0,
                    "retrieval_success": 0,
                    "source_correctness": 0,
                    "answer_acceptable": 0,
                }
            category_breakdown[cat]["total"] += 1

            if res["retrieval_success"]:
                retrieved_relevant_count += 1
                category_breakdown[cat]["retrieval_success"] += 1

            if res["source_correctness"]:
                correct_source_count += 1
                category_breakdown[cat]["source_correctness"] += 1

            if res["is_acceptable"]:
                answer_acceptable_count += 1
                category_breakdown[cat]["answer_acceptable"] += 1

            if res["is_multimodal"]:
                multimodal_total += 1
                if res["is_acceptable"] and res["source_correctness"]:
                    multimodal_successful += 1

            if res["failure_type"]:
                failure_cases.append({
                    "id": res["id"],
                    "category": res["category"],
                    "question": res["question"],
                    "failure_type": res["failure_type"],
                    "missing_sources": res["missing_sources"],
                    "missing_facts": res["missing_facts"],
                })

        summary = {
            "total_questions": total_questions,
            "retrieved_relevant_source": retrieved_relevant_count,
            "retrieval_success_rate": round(retrieved_relevant_count / max(1, total_questions), 3),
            "correct_source": correct_source_count,
            "source_correctness_rate": round(correct_source_count / max(1, total_questions), 3),
            "answer_acceptable": answer_acceptable_count,
            "answer_acceptable_rate": round(answer_acceptable_count / max(1, total_questions), 3),
            "multimodal_questions": multimodal_total,
            "multimodal_successful": multimodal_successful,
            "category_breakdown": category_breakdown,
            "failure_count": len(failure_cases),
            "failure_cases": failure_cases,
        }

        return {
            "summary": summary,
            "detailed_results": detailed_results,
        }
