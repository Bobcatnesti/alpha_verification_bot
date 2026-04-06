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

import requests
import json
import sys
import phonenumbers
from phonenumbers import carrier, geocoder

async def send_sms_message(mobile_no, message):
    parsed_no = phonenumbers.parse(mobile_no, "PH")
    
    if not phonenumbers.is_valid_number(parsed_no) and not phonenumbers.is_possible_number(parsed_no):
        
        sys.exit(1)

    url = "https://smsapiph.onrender.com/api/v1/send/sms"
    headers = {
        "x-api-key": "YOUR_API_KEY", # just need to add the api later and this should work
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": "parsed_no",
        "message": message
    }

    response = requests.post(url, headers=headers, json=payload)

    return response.json()