import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

# ----------------- CONFIG -----------------

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HF_TOKEN = os.getenv("HF_TOKEN")   # 🔐 Hugging Face token

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ----------------- QUOTE GENERATOR -----------------

def get_daily_quote():
    try:
        url = "https://api-inference.huggingface.co/models/gpt2"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": "Write a short motivational quote about career success:"}

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        quote = data[0]["generated_text"].replace("Write a short motivational quote about career success:", "").strip()
        return quote

    except:
        return "Success is built one application at a time."

# ----------------- HELPERS -----------------

def clean(text):
    return text.strip().replace("\n", " ").replace("\t", " ")

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

# ----------------- SCRAPERS (UNCHANGED) -----------------

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

    for card in soup.select("div, a"):
        text = clean(card.get_text())
        href = card.get("href", "")
        if "job" in text.lower() and len(text) > 12:
            link = href if href.startswith("http") else "https://www.ulcyberpark.com" + href
            jobs.append({"title": text, "company": "Cyberpark", "link": link})

    return jobs

# ----------------- MAILER -----------------

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"
    quote = get_daily_quote()

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

# ----------------- MAIN -----------------

if __name__ == "__main__":
    jobs = []
    jobs += get_infopark_jobs()
    jobs += get_technopark_jobs()
    jobs += get_cyberpark_jobs()
    send_email(jobs)
