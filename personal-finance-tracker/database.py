import sqlite3

DB_NAME = "finance.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_transaction(date, type_, category, amount, note):
    conn = get_conn()
    conn.execute(
        "INSERT INTO transactions (date, type, category, amount, note) VALUES (?, ?, ?, ?, ?)",
        (date, type_, category, amount, note)
    )
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM transactions ORDER BY date DESC").fetchall()
    conn.close()
    return rows

def delete_transaction(txn_id):
    conn = get_conn()
    conn.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
    conn.commit()
    conn.close()

def update_transaction(txn_id, date, type_, category, amount, note):
    conn = get_conn()
    conn.execute(
        "UPDATE transactions SET date=?, type=?, category=?, amount=?, note=? WHERE id=?",
        (date, type_, category, amount, note, txn_id)
    )
    conn.commit()
    conn.close()

def delete_all_transactions():
    conn = get_conn()
    conn.execute("DELETE FROM transactions")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
    conn.commit()
    conn.close()

def seed_sample_data():
    sample = [
        ("2026-06-01", "Income", "Salary", 45000, "Monthly salary"),
        ("2026-06-03", "Expense", "Rent", 12000, "House rent"),
        ("2026-06-05", "Expense", "Groceries", 3200, "Monthly groceries"),
        ("2026-06-10", "Expense", "Transport", 1500, "Fuel + cab"),
        ("2026-07-01", "Income", "Salary", 45000, "Monthly salary"),
        ("2026-07-02", "Expense", "Rent", 12000, "House rent"),
        ("2026-07-06", "Expense", "Groceries", 3600, "Monthly groceries"),
        ("2026-07-08", "Expense", "Entertainment", 1200, "Movies"),
        ("2026-07-12", "Expense", "Transport", 1800, "Fuel"),
        ("2026-07-15", "Income", "Freelance", 8000, "Side project"),
    ]
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO transactions (date, type, category, amount, note) VALUES (?, ?, ?, ?, ?)",
            sample
        )
        conn.commit()
    conn.close()
