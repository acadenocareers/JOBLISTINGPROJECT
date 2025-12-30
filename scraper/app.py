import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import random

# ===================== ENV =====================

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")
HF_TOKEN   = os.getenv("HF_TOKEN")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ===================== DEFAULT FALLBACK QUOTES =====================

DEFAULT_QUOTES = [
    "Success is built one application at a time.",
    "Great careers begin with brave applications.",
    "Consistency beats talent when talent doesn’t work.",
    "Small steps today lead to big success tomorrow.",
    "Your future is created by what you do today."
]

# ===================== AI QUOTE =====================

def get_ai_quote():
    try:
        url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        payload = {"inputs": "Write one short motivational career quote."}

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        data = response.json()

        if isinstance(data, list) and "summary_text" in data[0]:
            return data[0]["summary_text"].strip()
    except:
        pass

    return random.choice(DEFAULT_QUOTES)

# ===================== UTILS =====================

def clean(text):
    return text.strip().replace("\n", " ").replace("\t", " ")

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

# ===================== SCRAPERS =====================

def get_infopark_jobs():
    soup = fetch("https://infopark.in/companies/job-search")
    jobs = []

    for a in soup.select("a"):
        href = a.get("href", "")
        text = clean(a.get_text())
        if "/company/" in href and "/job/" in href and len(text) > 10:
            jobs.append({"title": text, "company": "Infopark", "link": "https://infopark.in" + href})

    return jobs

def get_technopark_jobs():
    soup = fetch("https://technopark.in/job-search")
    jobs = []

    for a in soup.select("a"):
        href = a.get("href", "")
        text = clean(a.get_text())
        if "/job/" in href and len(text) > 10:
            jobs.append({"title": text, "company": "Technopark", "link": "https://technopark.in" + href})

    return jobs

def get_cyberpark_jobs():
    soup = fetch("https://www.ulcyberpark.com/jobs")
    jobs = []

    for a in soup.select("a"):
        text = clean(a.get_text())
        href = a.get("href", "")
        if len(text) > 12 and "job" in text.lower():
            link = href if href.startswith("http") else "https://www.ulcyberpark.com" + href
            jobs.append({"title": text, "company": "Cyberpark", "link": link})

    return jobs

# ===================== MAIL =====================

def send_email(jobs):
    quote = get_ai_quote()
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"

    body = f"{quote}\n\n"

    if not jobs:
        body += "No jobs found today."
    else:
        for j in jobs[:40]:
            body += f"{j['title']}\n{j['company']}\n{j['link']}\n\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("Mail sent with", len(jobs), "jobs.")

# ===================== MAIN =====================

if __name__ == "__main__":
    jobs = []
    jobs += get_infopark_jobs()
    jobs += get_technopark_jobs()
    jobs += get_cyberpark_jobs()

    print("Total jobs collected:", len(jobs))
    send_email(jobs)
