> [!CAUTION]
> I am not updating This README every time i code, so expect the information not up to date

# Alpha Verification Bot (WIP, this progect are scaffold current with no code on almost all the file's)

A Discord bot for automating student verification in the server. Users submit their Student Assessment Invoice, the bot reads it using OCR, admins review it, and verified students get full server access through a multi-step role progression.

---

## How it works

1. User joins → assigned **Unverified** role (restricted access)
2. User uploads their Student Assessment Invoice
3. Bot processes the document using OCR (extracts name, student number, etc.)
4. Extracted data is posted to the admin forum channel for review
5. Admin accepts, rejects, or edits the extracted data
6. If accepted → user gets **Pending** role
7. Admin sends a 2FA code to the user
8. User submits the code in Discord
9. If correct → user gets **Verified** role (full access)

---

## Project structure

```
alpha_verification_bot/
├── bot/
│   ├── features/         # discord commands (verification, admin, 2fa)
│   └── utils/            # embeds, role helpers
├── ocr/                  # document processing pipeline
├── database/             # models, queries, db connection
├── integrations/         # microsoft SMTP / Graph API, SMPP (WIP)
├── queue/                # rate-limited message queue + crash-safe state
├── storage/
│   ├── data/             # uploaded documents (gitignored)
│   └── temp/             # temporary processing files (gitignored)
├── main.py               # entry point
├── config.py             # loads .env settings
├── .env                  # your secrets (gitignored)
├── .env.example          # template for new team members
└── README.md
```

---

## Requirements

- Python 3.11
- [uv](https://github.com/astral-sh/uv) for package management
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed on your machine

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Bobcatnesti/alpha_verification_bot.git
cd alpha_verification_bot
```

### 2. Pin Python version

```bash
uv python pin 3.11
```

### 3. Create virtual environment

```bash
uv venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 4. Install dependencies

```bash
uv sync
```

### 5. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values. See [Environment Variables](#environment-variables) below.

### 6. Install Tesseract

Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

Then update `TESSERACT_PATH` in your `.env` to point to the install location.

### 7. Run the bot

```bash
python main.py
```

---

## Environment variables

| Variable | Description | Where to get it |
|---|---|---|
| `DISCORD_TOKEN` | Bot token | Developer Portal → Bot → Reset Token |
| `DISCORD_PERMISSIONS` | Permission integer | Developer Portal → OAuth2 → URL Generator |
| `GUILD_ID` | Your server ID | Right click server → Copy Server ID |
| `ADMIN_FORUM_CHANNEL_ID` | Admin review forum channel | Right click channel → Copy Channel ID |
| `UNVERIFIED_ROLE_ID` | Role 1 | Server Settings → Roles → right click → Copy Role ID |
| `PENDING_ROLE_ID` | Role 2 | Same as above |
| `VERIFIED_ROLE_ID` | Role 3 | Same as above |
| `DATABASE_URL` | DB connection string | Default: `sqlite:///verification.db` |
| `UPLOAD_PATH` | Where to save submitted docs | Default: `storage/data` |
| `TESSERACT_PATH` | Path to tesseract.exe | After installing Tesseract |
| `TWOFA_EXPIRY_MINUTES` | How long a 2FA code is valid | Any number, e.g. `10` |
| `QUEUE_STATE_PATH` | Path to queue state file | Default: `queue/state.json` |
| `SMPP_RATE_LIMIT` | Max SMS per minute | e.g. `10` |
| `MS_SMTP_EMAIL` | Org email for sending codes | Your org Microsoft 365 email *(WIP)* |
| `MS_SMTP_APP_PASSWORD` | App password for SMTP | Microsoft 365 admin settings *(WIP)* |
| `MS_CLIENT_ID` | Azure app client ID | Azure Portal → App registrations *(WIP)* |
| `MS_CLIENT_SECRET` | Azure app secret | Azure Portal → Certificates & secrets *(WIP)* |
| `MS_TENANT_ID` | Azure tenant ID | Azure Portal → App registrations *(WIP)* |

> Enable Developer Mode in Discord to copy IDs: Settings → Advanced → Developer Mode → on

---

## Discord bot setup

### Permissions required

**General:** Manage Roles, View Channels, Manage Channels

**Text:** Send Messages, Send Messages in Threads, Manage Messages, Manage Threads, Create Public Threads, Embed Links, Attach Files, Read Message History, Use Slash Commands, Add Reactions

### Role hierarchy

The bot's role must be **dragged to the top** of the role list in Server Settings → Roles. Without this it cannot assign roles to members.

### Privileged intents

In the Developer Portal → your app → Bot, enable:
- Server Members Intent
- Message Content Intent

---

## Packages used

| Package | Version | Purpose |
|---|---|---|
| `discord.py` | 2.7.1 | Discord bot framework |
| `python-dotenv` | 1.2.2 | Load `.env` variables |
| `sqlalchemy` | 2.0.49 | Database ORM |
| `aiosqlite` | 0.22.1 | Async SQLite driver |
| `pytesseract` | 0.3.13 | OCR engine wrapper |
| `pillow` | 12.2.0 | Image processing |
| `pymupdf` | 1.27.2 | PDF to image conversion |
| `aiofiles` | 25.1.0 | Async file I/O for queue state |
| `aiohttp` | 3.13.5 | HTTP client (future integrations) |

---

## Team ownership

| Folder | Area |
|---|---|
| `bot/features/` | Discord commands and events |
| `bot/utils/` | Shared bot helpers |
| `ocr/` | Document processing pipeline |
| `database/` | Data models and queries |
| `integrations/` | Email and SMS *(WIP)* |
| `queue/` | Rate-limited message queue |

---

## Notes

- `storage/data/` and `storage/temp/` are gitignored — documents are never committed
- `queue/state.json` is gitignored — holds live runtime state so the queue survives restarts
- `integrations/` is work in progress and not connected to the main flow yet
- Microsoft Graph API requires admin approval from your org's Microsoft 365 admin
