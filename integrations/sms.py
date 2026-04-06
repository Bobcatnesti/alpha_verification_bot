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