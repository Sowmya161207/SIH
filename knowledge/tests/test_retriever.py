import unittest
from knowledge.retriever import search_documents, format_citations, EvidenceRetriever
from knowledge.schemas import DocumentType


class TestKnowledgeRetrieval(unittest.TestCase):
    def setUp(self):
        self.retriever = EvidenceRetriever()

    def test_search_documents_basic(self):
        """Test basic document search on P-101 vibration manual."""
        res = search_documents("vibration causes on pump P-101", top_k=3)
        self.assertGreater(res.total_matched, 0)
        self.assertGreaterEqual(len(res.citations), 1)
        top_citation = res.citations[0]
        self.assertEqual(top_citation.equipment_tag, "P-101")
        self.assertIn("bearing", top_citation.text.lower())

    def test_metadata_filtering_equipment_tag(self):
        """Test filtering exclusively by equipment tag."""
        res = search_documents("temperature", filters={"equipment_tag": "P-101"})
        for c in res.citations:
            self.assertEqual(c.equipment_tag, "P-101")

    def test_metadata_filtering_doc_type(self):
        """Test filtering exclusively by document type."""
        res = search_documents("seal pressure test", filters={"doc_type": "MAINTENANCE_LOG"})
        for c in res.citations:
            self.assertEqual(c.doc_type, "MAINTENANCE_LOG")

    def test_format_citations(self):
        """Test citation markdown formatting."""
        res = search_documents("K-101 anti-surge minimum safe suction flow", top_k=1)
        formatted = format_citations(res.citations)
        self.assertIn("Evidence & Documentation Sources", formatted)
        self.assertIn("K-101", formatted)


if __name__ == "__main__":
    unittest.main()
