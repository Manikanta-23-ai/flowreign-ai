
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager


DATA_DIR = Path(
    os.getenv("FLOWREIGN_DATA_DIR", r"D:\FlowReignStorage\data")
)
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "flowreign.db"


@contextmanager
def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                objective TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                requires_approval INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                result TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS workflow_tasks (
                task_id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                title TEXT NOT NULL,
                assigned_agent TEXT NOT NULL,
                description TEXT NOT NULL,
                depends_on TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'planned',
                requires_human_approval INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                output TEXT,
                FOREIGN KEY(workflow_id) REFERENCES workflows(id)
            )
        """)

        # Safely migrate existing databases.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(workflow_tasks)"
            ).fetchall()
        }

        if "output" not in columns:
            connection.execute(
                "ALTER TABLE workflow_tasks ADD COLUMN output TEXT"
            )

        connection.execute("""
            CREATE TABLE IF NOT EXISTS workflow_approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL UNIQUE,
                decision TEXT NOT NULL,
                note TEXT,
                decided_at TEXT NOT NULL,
                FOREIGN KEY(workflow_id) REFERENCES workflows(id)
            )
        """)
