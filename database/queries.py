from .db import get_connection
import json
from datetime import datetime


# ---------------- USERS ----------------

def create_user(discord_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (discord_id)
    VALUES (?)
    """, (discord_id,))

    conn.commit()
    conn.close()


def get_user_by_discord(discord_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM users WHERE discord_id = ?
    """, (discord_id,))

    user = cursor.fetchone()
    conn.close()
    return user


# ---------------- APPLICATIONS ----------------

def create_application(user_id: int, ocr_data: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO applications (user_id, status, ocr_data)
    VALUES (?, 'submitted', ?)
    """, (user_id, json.dumps(ocr_data)))

    conn.commit()
    conn.close()


def update_application_status(app_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE applications
    SET status = ?
    WHERE id = ?
    """, (status, app_id))

    conn.commit()
    conn.close()


def approve_application(app_id: int, admin_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE applications
    SET status = '2fa_pending',
        reviewed_by = ?,
        reviewed_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (admin_id, app_id))

    conn.commit()
    conn.close()


def reject_application(app_id: int, admin_id: int, notes: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE applications
    SET status = 'rejected',
        reviewed_by = ?,
        reviewed_at = CURRENT_TIMESTAMP,
        notes = ?
    WHERE id = ?
    """, (admin_id, notes, app_id))

    conn.commit()
    conn.close()


# ---------------- 2FA ----------------

def create_2fa_code(user_id: int, code: str, expires_at: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO two_factor_codes (user_id, code, expires_at)
    VALUES (?, ?, ?)
    """, (user_id, code, expires_at))

    conn.commit()
    conn.close()


def verify_2fa_code(user_id: int, code: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM two_factor_codes
    WHERE user_id = ?
      AND code = ?
      AND expires_at > CURRENT_TIMESTAMP
      AND verified_at IS NULL
    """, (user_id, code))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return False

    cursor.execute("""
    UPDATE two_factor_codes
    SET verified_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (row["id"],))

    cursor.execute("""
    UPDATE applications
    SET status = 'verified',
        verified_at = CURRENT_TIMESTAMP
    WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()
    return True