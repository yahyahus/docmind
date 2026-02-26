from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4N2Y3NzI5NC1kMmFhLTRmZDMtYmY5ZC01MGNiY2RjNDc4YmEiLCJleHAiOjE3NzIwNTc4MzIsInR5cGUiOiJhY2Nlc3MifQ.0Wh24MUh16wvXkpLF8koOGfagFQzcedkGt5jd4KTVDQ"

try:
    payload = jwt.decode(token, os.getenv("SECRET_KEY", "changethisinproduction"), algorithms=["HS256"])
    print("Token is valid!")
    print(payload)
except Exception as e:
    print(f"Token error: {e}")