import httpx
import config
import smtplib
from email.message import EmailMessage
import asyncio

SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587

async def get_access_token():
    url = f"https://login.microsoftonline.com/{config.MS_TENANT_ID}/oauth2/v2.0/token"

    data = {
        "client_id": config.MS_CLIENT_ID,
        "client_secret": config.MS_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()["access_token"]
    
async def send_email_via_smtp(to_email: str, subject: str, content: str):
    def _send():
        msg = EmailMessage()
        msg["From"] = config.EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(content)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            smtp.send_message(msg)

    await asyncio.to_thread(_send)

async def send_email_via_graph( access_token: str, to_email: str, subject: str, content: str, from_user: str = None ):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": content
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email
                    }
                }
            ]
        },
        "saveToSentItems": True
    }

    async with httpx.AsyncClient() as client:
        if from_user:
            url_b = f"https://graph.microsoft.com/v1.0/users/{from_user}/sendMail"
            response = await client.post(url_b, headers=headers, json=body)

            if response.status_code == 202:
                return {"status": "sent", "method": "graph_user"}
            
        url_a = "https://graph.microsoft.com/v1.0/me/sendMail"
        response = await client.post(url_a, headers=headers, json=body)

        if response.status_code == 202:
            return {"status": "sent", "method": "graph_me"}

        raise Exception(f"Graph API error (B then A failed): {response.status_code} - {response.text}")

async def send_message_via_teams(access_token: str, chat_id: str, content: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
        
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"

    body = {
        "body": {
            "content": content
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)

        if response.status_code not in (200, 201):
            raise Exception(response.text)

        return response.json()

async def get_user_by_email(access_token: str, email: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:

        url = f"https://graph.microsoft.com/v1.0/users/{email}"
        response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()

        url = f"https://graph.microsoft.com/v1.0/users?$filter=mail eq '{email}'"
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Graph API error: {response.text}")

        data = response.json()

        if not data.get("value"):
            raise Exception("User not found")

        return data["value"][0]

async def create_chat_with_user(access_token: str, owner_id: str, user_id: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    #  https://graph.microsoft.com/v1.0/me/ for the owner id or with the mail
    url = "https://graph.microsoft.com/v1.0/chats"

    body = {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{owner_id}')"
            },
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{user_id}')"
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)

        if response.status_code not in (200, 201):
            raise Exception(response.text)

        return response.json()