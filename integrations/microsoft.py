"""
microsoft.py — Microsoft Graph API & SMTP utilities.

Covers:
  - OAuth2 token acquisition (client credentials flow)
  - Email sending via SMTP (Office 365) or Microsoft Graph
  - Teams chat messaging
  - User and chat management via Graph
"""

import asyncio
import logging
import smtplib
from email.message import EmailMessage
from typing import Literal

import httpx

import config


logger = logging.getLogger(__name__)


SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class MicrosoftAuthError(Exception):
    """Raised when OAuth2 token acquisition fails."""

class GraphAPIError(Exception):
    """Raised when a Microsoft Graph API call returns an unexpected status."""
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code

class UserNotFoundError(GraphAPIError):
    """Raised when a Graph user lookup returns no results."""

class SMTPSendError(Exception):
    """Raised when an SMTP send operation fails."""


async def get_access_token() -> str:
    """
    Obtain an OAuth2 access token using the client credentials flow.

    Returns:
        The raw access token string.

    Raises:
        MicrosoftAuthError: If the token endpoint returns a non-200 response.
    """
    url = f"https://login.microsoftonline.com/{config.MS_TENANT_ID}/oauth2/v2.0/token"
    payload = {
        "client_id": config.MS_CLIENT_ID,
        "client_secret": config.MS_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)

    if response.status_code != 200:
        raise MicrosoftAuthError(
            f"Token request failed [{response.status_code}]: {response.text}"
        )

    token: str = response.json()["access_token"]
    logger.debug("Access token acquired successfully.")
    return token

async def send_email_via_smtp( to_email: str, subject: str, content: str, *, content_type: Literal["plain", "html"] = "plain", ) -> None:
    """
    Send an email through Office 365 SMTP with STARTTLS.

    Args:
        to_email:     Recipient address.
        subject:      Email subject line.
        content:      Body text (plain or HTML).
        content_type: ``"plain"`` (default) or ``"html"``.

    Raises:
        SMTPSendError: If the SMTP handshake or send operation fails.
    """
    def _send() -> None:
        msg = EmailMessage()
        msg["From"] = config.EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        if content_type == "html":
            msg.add_alternative(content, subtype="html")
        else:
            msg.set_content(content)

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
                smtp.send_message(msg)
                logger.info("Email sent via SMTP to %s", to_email)
        except smtplib.SMTPException as exc:
            raise SMTPSendError(f"SMTP send failed: {exc}") from exc

    await asyncio.to_thread(_send)

def _build_email_body( to_email: str, subject: str, content: str, content_type: Literal["Text", "HTML"] = "Text", ) -> dict:
    """Return the JSON body for a Graph sendMail request."""
    return {
        "message": {
            "subject": subject,
            "body": {"contentType": content_type, "content": content},
            "toRecipients": [{"emailAddress": {"address": to_email}}],
        },
        "saveToSentItems": True,
    }

async def send_email_via_graph( access_token: str, to_email: str, subject: str, content: str, from_user: str | None = None, content_type: Literal["Text", "HTML"] = "Text", ) -> dict:
    """
    Send an email using the Microsoft Graph API.

    Tries ``/users/{from_user}/sendMail`` first when *from_user* is supplied,
    then falls back to ``/me/sendMail``.

    Args:
        access_token: A valid Graph bearer token.
        to_email:     Recipient address.
        subject:      Email subject line.
        content:      Body content.
        from_user:    Optional sender UPN or object ID for delegated sending.
        content_type: ``"Text"`` (default) or ``"HTML"``.

    Returns:
        A dict with ``{"status": "sent", "method": "<graph_user|graph_me>"}``.

    Raises:
        GraphAPIError: If all send attempts fail.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = _build_email_body(to_email, subject, content, content_type)

    async with httpx.AsyncClient() as client:
        if from_user:
            url = f"{GRAPH_BASE}/users/{from_user}/sendMail"
            response = await client.post(url, headers=headers, json=body)

            if response.status_code == 202:
                logger.info("Email sent via Graph (user: %s) to %s", from_user, to_email)
                return {"status": "sent", "method": "graph_user"}

            logger.warning(
                "Graph /users/%s/sendMail failed [%s]; falling back to /me.",
                from_user,
                response.status_code,
            )

        url = f"{GRAPH_BASE}/me/sendMail"
        response = await client.post(url, headers=headers, json=body)

        if response.status_code == 202:
            logger.info("Email sent via Graph (/me) to %s", to_email)
            return {"status": "sent", "method": "graph_me"}

        raise GraphAPIError(
            f"Graph sendMail failed [{response.status_code}]: {response.text}",
            status_code=response.status_code,
        )

async def send_message_via_teams( access_token: str, chat_id: str, content: str, content_type: Literal["text", "html"] = "text", ) -> dict:
    """
    Post a message to a Teams one-on-one or group chat.

    Args:
        access_token: A valid Graph bearer token.
        chat_id:      The Teams chat ID.
        content:      Message body.
        content_type: ``"text"`` (default) or ``"html"``.

    Returns:
        The Graph API response as a dict.

    Raises:
        GraphAPIError: On a non-2xx response.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = f"{GRAPH_BASE}/chats/{chat_id}/messages"
    body = {"body": {"contentType": content_type, "content": content}}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)

    if response.status_code not in (200, 201):
        raise GraphAPIError(
            f"Teams message failed [{response.status_code}]: {response.text}",
            status_code=response.status_code,
        )

    logger.info("Teams message posted to chat %s", chat_id)
    return response.json()

async def get_user_by_email(access_token: str, email: str) -> dict:
    """
    Look up a Microsoft 365 user by email address.

    Tries a direct UPN/ID lookup first, then falls back to a ``$filter`` query.

    Args:
        access_token: A valid Graph bearer token.
        email:        The user's email / UPN.

    Returns:
        The Graph user object as a dict.

    Raises:
        UserNotFoundError: If no matching user is found.
        GraphAPIError:     On unexpected API errors.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GRAPH_BASE}/users/{email}", headers=headers
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code not in (400, 404):
            raise GraphAPIError(
                f"Direct user lookup failed [{response.status_code}]: {response.text}",
                status_code=response.status_code,
            )

        response = await client.get(
            f"{GRAPH_BASE}/users?$filter=mail eq '{email}'",
            headers=headers,
        )

    if response.status_code != 200:
        raise GraphAPIError(
            f"Filtered user lookup failed [{response.status_code}]: {response.text}",
            status_code=response.status_code,
        )

    users = response.json().get("value", [])
    if not users:
        raise UserNotFoundError(f"No user found for email: {email}")

    return users[0]

async def get_or_create_chat( access_token: str, owner_id: str, user_id: str, ) -> dict:
    """
    Return an existing one-on-one Teams chat or create one if it doesn't exist.

    Args:
        access_token: A valid Graph bearer token.
        owner_id:     Object ID of the initiating user.
        user_id:      Object ID of the other participant.

    Returns:
        The Graph chat object as a dict.

    Raises:
        GraphAPIError: On a non-2xx response.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    def _member(user_oid: str, role: str = "owner") -> dict:
        return {
            "@odata.type": "#microsoft.graph.aadUserConversationMember",
            "roles": [role],
            "user@odata.bind": f"{GRAPH_BASE}/users('{user_oid}')",
        }

    body = {
        "chatType": "oneOnOne",
        "members": [_member(owner_id), _member(user_id)],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GRAPH_BASE}/chats", headers=headers, json=body
        )

    if response.status_code not in (200, 201):
        raise GraphAPIError(
            f"Chat creation failed [{response.status_code}]: {response.text}",
            status_code=response.status_code,
        )

    logger.info("Chat retrieved/created between %s and %s", owner_id, user_id)
    return response.json()