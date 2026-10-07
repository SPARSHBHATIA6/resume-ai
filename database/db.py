"""SQLite persistence for lightweight analysis history."""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List

DB_PATH = Path(__file__).resolve().parent / "resumeai.db"


def get_connection():
    """Open a SQLite connection with row access."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the analysis table if it does not exist."""
    with get_connection() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                resume_name TEXT NOT NULL,
                match_score REAL NOT NULL,
                matched_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL
            )"""
        )
        conn.commit()


def save_analysis(resume_name: str, match_score: float, matched: List[str], missing: List[str]) -> int:
    """Save metadata only; the uploaded PDF itself is never stored."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO analyses (resume_name, match_score, matched_skills, missing_skills) VALUES (?, ?, ?, ?)",
            (resume_name, match_score, json.dumps(matched), json.dumps(missing)),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_analyses(limit: int = 20) -> List[Dict]:
    """Return recent analysis metadata."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def delete_history() -> None:
    """Delete analysis metadata history."""
    with get_connection() as conn:
        conn.execute("DELETE FROM analyses")
        conn.commit()
