import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "app.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id INTEGER UNIQUE NOT NULL,

        student_number TEXT UNIQUE,
        full_name TEXT,
        email TEXT,
        program TEXT,
        branch TEXT,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # APPLICATIONS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,

        status TEXT NOT NULL CHECK (status IN (
            'submitted',
            'approved',
            'rejected',
            '2fa_pending',
            'verified'
        )),

        ocr_data TEXT,
        extracted_name TEXT,
        extracted_student_number TEXT,

        reviewed_by INTEGER,
        reviewed_at DATETIME,
        notes TEXT,

        submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        verified_at DATETIME,

        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # 2FA
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS two_factor_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,

        code TEXT NOT NULL,
        expires_at DATETIME NOT NULL,
        verified_at DATETIME,

        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # INDEXES
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_discord_id ON users(discord_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_user_id ON applications(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_2fa_user_id ON two_factor_codes(user_id);")

    conn.commit()
    conn.close()