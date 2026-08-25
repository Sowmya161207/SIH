import sqlite3
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Resolve the database path relative to the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "users.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Establish and return a connection to the SQLite database.
    Ensures the data directory exists.
    """
    if not DB_DIR.exists():
        DB_DIR.mkdir(parents=True, exist_ok=True)
        
    conn = sqlite3.connect(str(DB_PATH))
    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    return conn


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user from the SQLite database by their username.
    Only returns the user if they are active.
    
    Parameters
    ----------
    username : str
        The username to look up
        
    Returns
    -------
    Optional[Dict[str, Any]]
        The user dictionary if found and active, otherwise None.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Fetch user by username where active
            cursor.execute(
                "SELECT username, password_hash, role FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            
            return None
    except sqlite3.Error as e:
        logger.error(f"Database error while fetching user {username}: {e}")
        return None
