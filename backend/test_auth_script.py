import asyncio
from httpx import AsyncClient
from app.main import app
import sqlite3
from app.db.database import get_db_connection

async def test_auth():
    # Because FastAPI 0.110 AsyncClient can take transport instead of app, we will use ASGITransport
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # TEST 1: operator login
        print("TEST 1: operator login")
        res = await client.post("/api/auth/login", json={"username": "operator", "password": "operator_demo"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        operator_token = data["access_token"]
        assert data["user"]["role"] == "operator"
        print("[OK] Passed")

        # TEST 2: supervisor login
        print("TEST 2: supervisor login")
        res = await client.post("/api/auth/login", json={"username": "supervisor", "password": "supervisor_demo"})
        assert res.status_code == 200
        assert res.json()["user"]["role"] == "supervisor"
        print("[OK] Passed")

        # TEST 3: viewer login
        print("TEST 3: viewer login")
        res = await client.post("/api/auth/login", json={"username": "viewer", "password": "viewer_demo"})
        assert res.status_code == 200
        assert res.json()["user"]["role"] == "viewer"
        print("[OK] Passed")

        # TEST 4: wrong password
        print("TEST 4: wrong password")
        res = await client.post("/api/auth/login", json={"username": "operator", "password": "wrongpassword"})
        assert res.status_code == 401
        print("[OK] Passed")

        # TEST 5: unknown username
        print("TEST 5: unknown username")
        res = await client.post("/api/auth/login", json={"username": "unknownuser", "password": "operator_demo"})
        assert res.status_code == 401
        print("[OK] Passed")

        # TEST 6: inactive user
        print("TEST 6: inactive user")
        # Temporarily make viewer inactive
        with get_db_connection() as conn:
            conn.execute("UPDATE users SET is_active = 0 WHERE username = 'viewer'")
            conn.commit()
            
        res = await client.post("/api/auth/login", json={"username": "viewer", "password": "viewer_demo"})
        assert res.status_code == 401
        
        # Restore viewer
        with get_db_connection() as conn:
            conn.execute("UPDATE users SET is_active = 1 WHERE username = 'viewer'")
            conn.commit()
        print("[OK] Passed")

        # TEST 7: operator JWT -> protected Chat
        print("TEST 7: operator JWT -> protected Chat")
        res = await client.post(
            "/api/chat/message", 
            json={"message": "hello", "workspace_id": "ws-1", "document_ids": []}, 
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert res.status_code not in [401, 403], f"Failed auth with {res.status_code}, response: {res.text}"
        print("[OK] Passed")

        # TEST 8: user with insufficient role -> protected endpoint
        res_viewer = await client.post("/api/auth/login", json={"username": "viewer", "password": "viewer_demo"})
        viewer_token = res_viewer.json()["access_token"]
        
        print("TEST 8: insufficient role (viewer trying to upload)")
        res = await client.post(
            "/api/documents/upload",
            data={"workspace_id": "ws-1", "equipment": "test", "document_type": "manual", "classification": "internal"},
            files={"file": ("test.pdf", b"dummy content", "application/pdf")},
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert res.status_code == 403, f"Expected 403, got {res.status_code}"
        print("[OK] Passed")
        
        print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_auth())
