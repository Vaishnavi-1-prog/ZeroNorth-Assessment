import sqlite3
from datetime import datetime

DB_NAME = "tasks.db"


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the tasks table if it doesn't already exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,      -- Low / Medium / High
            due_date TEXT,               -- YYYY-MM-DD
            status TEXT NOT NULL,        -- To Do / In Progress / Done
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_task(title, description, priority, due_date, status="To Do"):
    conn = get_connection()
    conn.execute(
        """INSERT INTO tasks (title, description, priority, due_date, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, description, priority, due_date, status, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY due_date IS NULL, due_date ASC").fetchall()
    conn.close()
    return rows


def update_status(task_id, new_status):
    conn = get_connection()
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

#---------------
def update_task(task_id, title, description, priority, due_date):
    conn = get_connection()
    conn.execute(
        """UPDATE tasks SET title=?, description=?, priority=?, due_date=? WHERE id=?""",
        (title, description, priority, due_date, task_id),
    )
    conn.commit()
    conn.close()
