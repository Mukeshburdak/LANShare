import sqlite3

DB_NAME = "database/history.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filesize INTEGER,
        sender TEXT,
        receiver TEXT,
        status TEXT,
        transfer_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def add_history(filename, filesize, sender, receiver, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history(filename, filesize, sender, receiver, status)
    VALUES(?,?,?,?,?)
    """, (filename, filesize, sender, receiver, status))

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM history ORDER BY transfer_time DESC")

    rows = cursor.fetchall()

    conn.close()

    return rows
