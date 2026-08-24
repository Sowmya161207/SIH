import unittest
from security.audit import AuditLogger
from security.schemas import AuditEventType


class TestAuditLogger(unittest.TestCase):
    def setUp(self):
        self.logger = AuditLogger()

    def test_log_model_selected(self):
        """Test logging local model selection without leaking sensitive prompts."""
        event = self.logger.log_model_selected(
            model_name="llama3:8b-instruct",
            provider="Local Ollama @ localhost:11434",
            parameters={"temperature": 0.1, "max_tokens": 1024}
        )
        self.assertEqual(event.event_type, AuditEventType.MODEL_SELECTED)
        self.assertIn("llama3", event.resource_id)

    def test_log_document_processed_no_content_leakage(self):
        """Test that sensitive document body text is sanitized from audit logs."""
        sensitive_doc = "CONFIDENTIAL MRPL DISTILLATION VALVE SCHEDULE: TOP SECRET 120 DEGREE LIMIT"
        event = self.logger.log_event(
            event_type=AuditEventType.DOCUMENT_PROCESSED,
            action="Processed internal technical manual",
            resource_id="DOC-9921",
            details={
                "filename": "confidential_manual.pdf",
                "document_text": sensitive_doc,
                "pages": 12
            }
        )

        # Check sanitized details
        self.assertNotIn("TOP SECRET", json_str := str(event.details))
        self.assertIn("document_text_length", event.details)
        self.assertIn("REDACTED_FOR_AUDIT", event.details["document_text_preview"])

    def test_log_tool_executed(self):
        """Test tool execution audit recording."""
        event = self.logger.log_tool_executed(
            tool_name="verify_claims",
            execution_time_ms=1.45,
            caller="chat_service"
        )
        self.assertEqual(event.event_type, AuditEventType.TOOL_EXECUTED)
        self.assertEqual(event.resource_id, "verify_claims")


if __name__ == "__main__":
    unittest.main()
