import json
import os
import unittest


class TestEvaluationDataset(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "datasets"))
        self.json_path = os.path.join(self.base_dir, "p101_evaluation_dataset.json")
        self.jsonl_path = os.path.join(self.base_dir, "p101_evaluation_dataset.jsonl")

    def test_json_dataset_structure(self):
        """Verify the JSON evaluation dataset conforms to the required schema."""
        self.assertTrue(os.path.exists(self.json_path), f"File not found: {self.json_path}")

        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 10)

        types_found = set()
        required_fields = ["question", "expected_sources", "type", "expected_answer"]

        for item in data:
            # Check all required fields
            for field in required_fields:
                self.assertIn(field, item, f"Missing field '{field}' in item {item.get('id')}")

            # Check field types & values
            self.assertIsInstance(item["question"], str)
            self.assertGreater(len(item["question"].strip()), 0)

            self.assertIsInstance(item["expected_sources"], list)
            self.assertGreater(len(item["expected_sources"]), 0)

            self.assertIn(item["type"], ["text", "image", "multimodal"])
            types_found.add(item["type"])

            self.assertIsInstance(item["expected_answer"], str)
            self.assertGreater(len(item["expected_answer"].strip()), 0)

        # Verify all 3 types are covered
        self.assertEqual(types_found, {"text", "image", "multimodal"})

    def test_jsonl_dataset_structure(self):
        """Verify the JSONL dataset loads correctly line-by-line."""
        self.assertTrue(os.path.exists(self.jsonl_path), f"File not found: {self.jsonl_path}")

        lines_count = 0
        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                self.assertIn("question", item)
                self.assertIn("expected_sources", item)
                self.assertIn("type", item)
                self.assertIn("expected_answer", item)
                lines_count += 1

        self.assertGreaterEqual(lines_count, 10)


if __name__ == "__main__":
    unittest.main()
