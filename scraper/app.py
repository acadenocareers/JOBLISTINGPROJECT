import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import random

# ================= ENV =================

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")
HF_TOKEN   = os.getenv("HF_TOKEN")

# ================= QUOTE GENERATOR =================

DEFAULT_QUOTES = [
    "Success is built one application at a time.",
    "Great careers begin with brave applications.",
    "Your future is created by what you do today.",
    "Every job you apply to moves you forward.",
    "Consistency beats talent when talent doesn’t work."
]

def get_ai_quote():
    try:
        url = "https://api-inference.huggingface.co/models/google/flan-t5-small"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": "Generate one short motivational career quote."}

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()

    except Exception as e:
        print("Quote API error:", e)

    return random.choice(DEFAULT_QUOTES)

# ================= MAILER =================

def send_email():
    quote = get_ai_quote()
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"

    body = f"""
{quote}

No jobs found today.
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("Mail sent successfully.")

# ================= MAIN =================

if __name__ == "__main__":
    send_email()
