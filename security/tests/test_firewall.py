import unittest
from security.firewall import DataLeakageFirewall


class TestDataLeakageFirewall(unittest.TestCase):
    def setUp(self):
        self.firewall = DataLeakageFirewall(strict_mode=True)

    def test_allow_local_endpoints(self):
        """Verify localhost and local IP endpoints are permitted."""
        local_targets = [
            "http://localhost:11434/api/generate",
            "http://127.0.0.1:8000/api/chat",
            "http://0.0.0.0:6333",
            "http://192.168.1.50:8080",
            "http://10.0.0.12:9000",
            "http://backend:8000",
            "http://ollama:11434"
        ]
        for target in local_targets:
            is_allowed, reason = self.firewall.validate_destination(target)
            self.assertTrue(is_allowed, f"Failed on local target: {target} ({reason})")

    def test_block_cloud_ai_endpoints(self):
        """Verify known cloud AI endpoints are strictly blocked."""
        cloud_targets = [
            "https://api.openai.com/v1/chat/completions",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro",
            "https://api.anthropic.com/v1/messages",
            "https://api.cohere.ai/v1/generate",
            "https://api.mistral.ai/v1/chat/completions",
            "https://api.together.xyz/inference",
            "https://api.groq.com/openai/v1/chat/completions"
        ]
        for target in cloud_targets:
            is_allowed, reason = self.firewall.validate_destination(target)
            self.assertFalse(is_allowed, f"Cloud target should be blocked: {target}")
            self.assertIn("BLOCKED", reason)

    def test_block_public_internet_domains(self):
        """Verify generic external internet URLs are blocked in strict sovereign mode."""
        external_targets = [
            "https://google.com/search",
            "http://example.com/api",
            "https://93.184.216.34" # Public IP
        ]
        for target in external_targets:
            is_allowed, reason = self.firewall.validate_destination(target)
            self.assertFalse(is_allowed, f"External public target should be blocked: {target}")

    def test_interception_counter(self):
        """Verify blocked attempts count increments on violation."""
        initial_count = self.firewall.blocked_attempts_count
        res = self.firewall.check_and_intercept("https://api.openai.com/v1/chat/completions")
        self.assertFalse(res)
        self.assertEqual(self.firewall.blocked_attempts_count, initial_count + 1)


if __name__ == "__main__":
    unittest.main()
