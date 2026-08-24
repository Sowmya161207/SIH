import unittest
from security.monitor import SovereigntyMonitor
from security.schemas import AuditEventType


class TestSovereigntyMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = SovereigntyMonitor()

    def test_get_status_structure(self):
        """Verify get_status returns the exact required sovereign status payload."""
        status = self.monitor.get_status()

        required_keys = [
            "deployment_mode",
            "external_calls",
            "local_models",
            "local_vector_db",
            "internet_required",
            "security_status"
        ]
        for key in required_keys:
            self.assertIn(key, status)

        self.assertEqual(status["deployment_mode"], "LOCAL_AIR_GAPPED")
        self.assertEqual(status["external_calls"], 0)
        self.assertEqual(status["local_vector_db"], True)
        self.assertEqual(status["internet_required"], False)
        self.assertEqual(status["security_status"], "SECURE")
        self.assertIsInstance(status["local_models"], list)
        self.assertGreater(len(status["local_models"]), 0)

    def test_verify_destination_or_block(self):
        """Verify external call interception and security alert triggering."""
        # Allowed local call
        allowed = self.monitor.verify_destination_or_block("http://localhost:11434/api/tags")
        self.assertTrue(allowed)

        # Blocked external call
        blocked = self.monitor.verify_destination_or_block("https://api.openai.com/v1/chat/completions")
        self.assertFalse(blocked)

        # Check status after blocked attempt
        status = self.monitor.get_status()
        self.assertEqual(status["external_calls"], 0) # 0 calls left the system!
        self.assertEqual(status["blocked_attempts"], 1)
        self.assertEqual(status["security_status"], "ALERT_BLOCKED_EXTERNAL_CALL")

    def test_ui_summary_for_tharun(self):
        """Verify the exact formatted UI summary for Frontend display."""
        summary = self.monitor.get_ui_summary()
        self.assertEqual(summary["mode_badge"], "🟢 Local Mode")
        self.assertIn("External Calls: 0", summary["external_calls"])
        self.assertIn("Data Leaving System: None", summary["data_leaving_system"])


if __name__ == "__main__":
    unittest.main()
