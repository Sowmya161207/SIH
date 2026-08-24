import unittest
from knowledge.benchmark import run_retrieval_benchmark
from knowledge.qa_engine import answer_and_verify


class TestKnowledgeBenchmark(unittest.TestCase):
    def test_benchmark_suite(self):
        """Test retrieval benchmark evaluation metric outputs."""
        report = run_retrieval_benchmark(top_k=3)
        self.assertEqual(report["status"], "PASS")
        self.assertGreaterEqual(report["mrr"], 0.85)
        self.assertGreaterEqual(report["mean_recall_at_k"], 0.80)
        self.assertLessEqual(report["average_latency_ms"], 100.0)

    def test_qa_pipeline_integration(self):
        """Test full answer_and_verify workflow combining retrieval and verification."""
        output = answer_and_verify(
            query="What is the high-high alarm temperature for P-101 motor?",
            filters={"equipment_tag": "P-101"},
            telemetry_context=["Telemetry: P-101 motor temperature is 130 deg C"]
        )
        self.assertIn("verification", output)
        self.assertGreater(len(output["citations"]), 0)


if __name__ == "__main__":
    unittest.main()
