"""
Unit Tests for Industrial RAG Evaluation Framework.
SIH PS 26117.
"""

import unittest
from pathlib import Path

from evaluation.dataset import load_industrial_test_set
from evaluation.engine.document_indexer import LocalDocumentIndexer
from evaluation.engine.metrics import EvaluationMetrics
from evaluation.engine.evaluator import RAGEvaluator


class TestIndustrialEvaluation(unittest.TestCase):
    """Test suite covering dataset integrity, indexing, metric computation, and evaluation runner."""

    @classmethod
    def setUpClass(cls):
        cls.dataset = load_industrial_test_set()
        cls.indexer = LocalDocumentIndexer()
        cls.evaluator = RAGEvaluator(indexer=cls.indexer)

    def test_01_dataset_schema_and_categories(self):
        """Verify dataset contains 25 items across all 7 mandatory industrial categories."""
        questions = self.dataset.get("questions", [])
        self.assertEqual(len(questions), 25)

        required_categories = {
            "Equipment specifications",
            "Maintenance",
            "Incident analysis",
            "SOP/procedure",
            "Cross-document reasoning",
            "P&ID/image questions",
            "Multimodal questions",
        }
        present_categories = {q["category"] for q in questions}
        self.assertEqual(required_categories, present_categories)

        for q in questions:
            self.assertIn("id", q)
            self.assertIn("question", q)
            self.assertIn("expected_source", q)
            self.assertGreater(len(q["expected_source"]), 0)
            self.assertIn("expected_key_facts", q)
            self.assertGreater(len(q["expected_key_facts"]), 0)
            self.assertIn("reference_answer", q)
            self.assertIn("is_multimodal", q)

    def test_02_indexer_documents(self):
        """Verify indexer contains indexed chunks from all 4 Pump P-101 PDFs."""
        indexed_docs = {c["doc_name"] for c in self.indexer.chunks}
        expected_docs = {
            "Pump_P101_Equipment_Manual.pdf",
            "Pump_P101_Incident_Report.pdf",
            "Pump_P101_Maintenance_Report.pdf",
            "Pump_P101_SOP.pdf",
        }
        self.assertEqual(expected_docs, indexed_docs)
        self.assertGreaterEqual(len(self.indexer.chunks), 20)

    def test_03_search_functionality(self):
        """Verify search finds relevant chunks for a specific equipment query."""
        results = self.indexer.search("What is the rated flow and motor power for P-101?", top_k=3)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["doc_name"], "Pump_P101_Equipment_Manual.pdf")
        self.assertIn("120 m³/h", results[0]["text"])

    def test_04_metric_calculations(self):
        """Verify retrieval and fact scoring metrics calculate accurately."""
        # Retrieval metric test
        mock_retrieved = [
            {"doc_name": "Pump_P101_Equipment_Manual.pdf", "page": 1},
            {"doc_name": "Pump_P101_SOP.pdf", "page": 3},
        ]
        ret_eval = EvaluationMetrics.evaluate_retrieval(
            mock_retrieved,
            expected_sources=["Pump_P101_Equipment_Manual.pdf"],
            expected_pages=[1],
        )
        self.assertTrue(ret_eval["retrieval_success"])
        self.assertTrue(ret_eval["source_correctness"])
        self.assertTrue(ret_eval["page_matched"])

        # Fact coverage test
        mock_text = "The pump has a rated flow of 120 m³/h and 30 kW motor."
        fact_eval = EvaluationMetrics.evaluate_answer_facts(
            mock_text, expected_key_facts=["120 m³/h", "30 kW", "missing_value"]
        )
        self.assertAlmostEqual(fact_eval["fact_coverage"], 2 / 3, places=2)
        self.assertIn("120 m³/h", fact_eval["matched_facts"])
        self.assertIn("missing_value", fact_eval["missing_facts"])

    def test_05_full_evaluator_run(self):
        """Execute full benchmark and verify summary aggregations."""
        results = self.evaluator.run_all(top_k=4)
        summary = results["summary"]

        self.assertEqual(summary["total_questions"], 25)
        self.assertGreaterEqual(summary["retrieved_relevant_source"], 20)
        self.assertGreaterEqual(summary["correct_source"], 18)
        self.assertGreaterEqual(summary["answer_acceptable"], 18)
        self.assertEqual(summary["multimodal_questions"], 2)
        self.assertEqual(len(results["detailed_results"]), 25)


if __name__ == "__main__":
    unittest.main()
