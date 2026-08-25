import sqlite3
import logging
from app.db.database import get_db_connection
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Demo users to seed into the database
DEMO_USERS = [
    {
        "username": "operator",
        "password": "operator_demo",
        "role": "operator"
    },
    {
        "username": "supervisor",
        "password": "supervisor_demo",
        "role": "supervisor"
    },
    {
        "username": "viewer",
        "password": "viewer_demo",
        "role": "viewer"
    }
]


def init_db():
    """
    Initialize the SQLite database and seed it with demo users.
    """
    logger.info("Initializing SQLite database...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Create the users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info("Users table is ready.")
        
        # 2. Seed the demo users safely
        for user in DEMO_USERS:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (user["username"],))
            existing_user = cursor.fetchone()
            
            if not existing_user:
                logger.info(f"Seeding demo user: {user['username']}")
                hashed_password = get_password_hash(user["password"])
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, is_active)
                    VALUES (?, ?, ?, 1)
                """, (user["username"], hashed_password, user["role"]))
            else:
                logger.info(f"Demo user '{user['username']}' already exists. Skipping.")
                
        conn.commit()
        logger.info("Database initialization completed successfully.")


if __name__ == "__main__":
    init_db()
