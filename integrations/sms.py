# https://smsapiph.netlify.app/documentation#quickstart

# # Send message with auto-fallback (Python)
# import requests
# import json

# url = "https://smsapiph.onrender.com/api/v1/send/sms"
# headers = {
#     "x-api-key": "YOUR_API_KEY",
#     "Content-Type": "application/json"
# }
# payload = {
#     "recipient": "+639#########",
#     "message": "Your verification code is 123456"
# }

# response = requests.post(url, headers=headers, json=payload)

# # Intelligent fallback:
# # 1. Try SMS
# # 2. If SMS fails → Try Email
# # 3. If Email fails → Send Push Notification

# data = response.json()

import httpx
import phonenumbers

async def send_sms_via_smpp(mobile_no: str, message: str) -> dict:
    parsed_no = phonenumbers.parse(mobile_no, "PH")

    # Validate number
    if not phonenumbers.is_valid_number(parsed_no) or not phonenumbers.is_possible_number(parsed_no):
        raise ValueError("Invalid phone number")

    # Convert to international format (E.164)
    formatted_number = phonenumbers.format_number(
        parsed_no, phonenumbers.PhoneNumberFormat.E164
    )

    url = "https://smsapiph.onrender.com/api/v1/send/sms"

    headers = {
        "x-api-key": "YOUR_API_KEY",
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": formatted_number,
        "message": message
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"SMS API error: {response.text}")

        return response.json()