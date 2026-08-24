import os
import unittest
from multimodal.processor import MultimodalDocumentProcessor
from multimodal.schemas import DiagramType
from multimodal.retriever import retrieve_multimodal_context


class TestMultimodalProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = MultimodalDocumentProcessor()

    def test_sample_diagrams_initialization(self):
        """Verify pre-registered P101 diagrams are loaded with metadata."""
        pages = self.processor.get_document_pages("MRPL-DOC-P101-BASE")
        self.assertEqual(len(pages), 3)

        # Page 1: P&ID
        page1 = self.processor.get_page("MRPL-DOC-P101-BASE", 1)
        self.assertIsNotNone(page1)
        self.assertEqual(page1.page_number, 1)
        self.assertEqual(page1.diagram_type, DiagramType.PID)
        self.assertTrue(page1.has_diagram)
        self.assertIn("P-101", page1.associated_equipment_tags)
        self.assertEqual(page1.image_id, "DWG-CDU-P101-PID-01")

        # Page 2: Mechanical Cross-Section
        page2 = self.processor.get_page("MRPL-DOC-P101-BASE", 2)
        self.assertEqual(page2.diagram_type, DiagramType.MECHANICAL_DRAWING)
        self.assertIn("NU 318", page2.extracted_text)

        # Page 3: Performance Curve
        page3 = self.processor.get_page("MRPL-DOC-P101-BASE", 3)
        self.assertEqual(page3.diagram_type, DiagramType.PERFORMANCE_CURVE)

    def test_document_ingestion_and_metadata_preservation(self):
        """Test ingesting a new document and verifying page metadata association."""
        doc_id = "TEST-DOC-P101-NEW"
        doc = self.processor.process_document(
            document_id=doc_id,
            filename="P101_Centrifugal_Pump_Piping_Diagram.pdf",
            text_content="Piping and Instrumentation Diagram for P-101 suction line",
            estimated_pages=2
        )

        self.assertEqual(doc.document_id, doc_id)
        self.assertEqual(doc.total_pages, 2)
        self.assertEqual(len(doc.pages), 2)

        # Check page association
        retrieved_pages = self.processor.get_document_pages(doc_id)
        self.assertEqual(len(retrieved_pages), 2)
        self.assertEqual(retrieved_pages[0].document_id, doc_id)
        self.assertEqual(retrieved_pages[0].page_number, 1)
        self.assertEqual(retrieved_pages[1].page_number, 2)
        self.assertEqual(retrieved_pages[0].diagram_type, DiagramType.PID)

        # Check on-disk metadata file
        meta_path = os.path.join(doc.storage_directory, "metadata.json")
        self.assertTrue(os.path.exists(meta_path))

    def test_multimodal_context_retrieval(self):
        """Test retrieving multimodal context combining text and image diagrams."""
        context = retrieve_multimodal_context(
            query="P-101 P&ID suction strainer and vibration transmitter location",
            equipment_tag="P-101",
            top_k_text=2,
            top_k_images=2
        )

        self.assertGreaterEqual(len(context.text_evidence), 1)
        self.assertGreaterEqual(len(context.page_images), 1)
        self.assertEqual(context.equipment_tags, ["P-101"])
        self.assertEqual(context.page_images[0].document_id, "MRPL-DOC-P101-BASE")


if __name__ == "__main__":
    unittest.main()
