import unittest
from fastapi.testclient import TestClient
import os
import sys

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.main import app

class TestSecurityRBAC(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_chat_without_auth(self):
        response = self.client.post("/api/chat", json={"message": "hello"})
        self.assertEqual(response.status_code, 403)

    def test_chat_with_invalid_auth(self):
        response = self.client.post("/api/chat", json={"message": "hello"}, headers={"Authorization": "Bearer invalid_token"})
        self.assertEqual(response.status_code, 401)

    def test_chat_with_valid_auth(self):
        response = self.client.post("/api/chat", json={"message": "hello"}, headers={"Authorization": "Bearer token_operator"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue("finding" in data or "answer" in data)

    def test_document_upload_requires_manager_or_admin(self):
        response = self.client.post(
            "/api/documents", 
            files={"file": ("test.pdf", b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF", "application/pdf")},
            headers={"Authorization": "Bearer token_operator"}
        )
        self.assertEqual(response.status_code, 403)

    def test_document_upload_success_for_manager(self):
        response = self.client.post(
            "/api/documents", 
            files={"file": ("test.pdf", b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF", "application/pdf")},
            headers={"Authorization": "Bearer token_manager"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("document_id", response.json())

    def test_cross_workspace_document_access(self):
        response = self.client.post(
            "/api/documents", 
            files={"file": ("test.pdf", b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF", "application/pdf")},
            headers={"Authorization": "Bearer token_manager"}
        )
        self.assertEqual(response.status_code, 200)
        doc_id = response.json()["document_id"]
        
        # Engineer from MRPL-MUM tries to access it
        response2 = self.client.get(f"/api/documents/{doc_id}", headers={"Authorization": "Bearer token_engineer"})
        self.assertEqual(response2.status_code, 403)
        
        # Manager from MRPL-BLR can access it
        response3 = self.client.get(f"/api/documents/{doc_id}", headers={"Authorization": "Bearer token_manager"})
        self.assertEqual(response3.status_code, 200)

if __name__ == "__main__":
    unittest.main()
