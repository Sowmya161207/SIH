import unittest
import os
import sys

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from knowledge.retriever import search_documents, _global_retriever
from knowledge.qa_engine import answer_and_verify
from knowledge.schemas import DocumentChunk, DocumentMetadata

class TestRAGEvaluation(unittest.TestCase):
    def setUp(self):
        # Inject some test documents with different workspaces and roles
        doc1 = DocumentChunk(
            chunk_id="TEST-1",
            text="Pump P-101 requires monthly vibration checks.",
            metadata=DocumentMetadata(
                doc_id="DOC-TEST-1",
                title="P-101 Maintenance Guide",
                doc_type="MAINTENANCE_LOG",
                unit="CDU-1",
                workspace_id="MRPL-BLR",
                allowed_roles=["Maintenance Engineer", "Manager"]
            )
        )
        doc2 = DocumentChunk(
            chunk_id="TEST-2",
            text="Financial projections for MRPL-MUM show 20% growth.",
            metadata=DocumentMetadata(
                doc_id="DOC-TEST-2",
                title="Q3 Financials",
                doc_type="SOP",
                unit="HQ",
                workspace_id="MRPL-MUM",
                allowed_roles=["Manager"]
            )
        )
        _global_retriever.add_documents([doc1, doc2])

    def test_correct_source_retrieval_authorized(self):
        # Manager in MRPL-BLR searches for P-101
        res = search_documents(
            "P-101 vibration", 
            filters={"workspace_id": "MRPL-BLR", "user_roles": ["Manager"]}
        )
        self.assertGreater(len(res.citations), 0)
        self.assertIn("TEST-1", [c.chunk_id for c in res.citations])
        self.assertNotIn("TEST-2", [c.chunk_id for c in res.citations])

    def test_wrong_workspace_access(self):
        # Manager in MRPL-BLR searches for financials (which is in MRPL-MUM)
        res = search_documents(
            "Financial projections", 
            filters={"workspace_id": "MRPL-BLR", "user_roles": ["Manager"]}
        )
        self.assertNotIn("TEST-2", [c.chunk_id for c in res.citations])

    def test_unauthorized_document_access(self):
        # Operator in MRPL-MUM searches for financials (needs Manager role)
        res = search_documents(
            "Financial projections", 
            filters={"workspace_id": "MRPL-MUM", "user_roles": ["Operator"]}
        )
        self.assertNotIn("TEST-2", [c.chunk_id for c in res.citations])

    def test_hallucination_insufficient_evidence(self):
        qa_result = answer_and_verify(
            "What is the top speed of a sports car?",
            workspace_id="MRPL-BLR",
            user_roles=["Manager"]
        )
        # Should result in insufficient evidence as it's not in knowledge base
        verification = qa_result["verification"]
        self.assertIn(verification["status"], ["INSUFFICIENT_EVIDENCE", "UNSUPPORTED"])
        self.assertLessEqual(verification["confidence"], 0.4)

    def test_citation_correctness(self):
        qa_result = answer_and_verify(
            "How often should P-101 be checked?",
            workspace_id="MRPL-BLR",
            user_roles=["Manager"]
        )
        self.assertGreater(len(qa_result["citations"]), 0)
        # Ensure citation has valid metadata
        titles = [c.get("document_title") for c in qa_result["citations"]]
        self.assertTrue(any("Maintenance" in t for t in titles))
        
if __name__ == "__main__":
    unittest.main()
