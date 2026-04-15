import os
from dotenv import load_dotenv

load_dotenv()

# ── Discord ────────────────────────────────────────────────
DISCORD_TOKEN        = os.getenv("DISCORD_TOKEN")
DISCORD_PERMISSIONS  = os.getenv("DISCORD_PERMISSIONS")
GUILD_ID             = int(os.getenv("GUILD_ID", 0))
ADMIN_FORUM_CHANNEL_ID = int(os.getenv("ADMIN_FORUM_CHANNEL_ID", 0))

# ── Roles ──────────────────────────────────────────────────
UNVERIFIED_ROLE_ID   = int(os.getenv("UNVERIFIED_ROLE_ID", 0))
PENDING_ROLE_ID      = int(os.getenv("PENDING_ROLE_ID", 0))
VERIFIED_ROLE_ID     = int(os.getenv("VERIFIED_ROLE_ID", 0))

# ── Database ───────────────────────────────────────────────
DATABASE_URL         = os.getenv("DATABASE_URL", "sqlite:///storage/data/verification.db")

# ── Storage ────────────────────────────────────────────────
UPLOAD_PATH          = os.getenv("UPLOAD_PATH", "storage/data")

# ── OCR ────────────────────────────────────────────────────
TESSERACT_PATH       = os.getenv("TESSERACT_PATH", "")

# ── 2FA ────────────────────────────────────────────────────
TWOFA_EXPIRY_MINUTES = int(os.getenv("TWOFA_EXPIRY_MINUTES", 10))

# ── Queue ──────────────────────────────────────────────────
QUEUE_STATE_PATH     = os.getenv("QUEUE_STATE_PATH", "queue/state.json")
SMPP_RATE_LIMIT      = int(os.getenv("SMPP_RATE_LIMIT", 10))
MS_RATE_LIMIT        = int(os.getenv("MS_RATE_LIMIT", 30))
QUEUE_INTERVAL       = int(os.getenv("QUEUE_INTERVAL", 5))

# ── SMPP (WIP) ─────────────────────────────────────────────
SMPP_HOST            = os.getenv("SMPP_HOST", "")
SMPP_PORT            = int(os.getenv("SMPP_PORT", 2775))
SMPP_USERNAME        = os.getenv("SMPP_USERNAME", "")
SMPP_PASSWORD        = os.getenv("SMPP_PASSWORD", "")
SMPP_SOURCE_ADDR     = os.getenv("SMPP_SOURCE_ADDR", "")

# ── Microsoft (WIP) ────────────────────────────────────────
MS_SMTP_EMAIL        = os.getenv("MS_SMTP_EMAIL", "")
MS_SMTP_APP_PASSWORD = os.getenv("MS_SMTP_APP_PASSWORD", "")
MS_CLIENT_ID         = os.getenv("MS_CLIENT_ID", "")
MS_CLIENT_SECRET     = os.getenv("MS_CLIENT_SECRET", "")
MS_TENANT_ID         = os.getenv("MS_TENANT_ID", "")