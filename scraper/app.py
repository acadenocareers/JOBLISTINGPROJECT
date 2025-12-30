import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import json

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")
HF_API_KEY = os.getenv("HF_API_KEY")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ---------------- UTILS ----------------

def clean(text):
    return text.strip().replace("\n", " ").replace("\t", " ")

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

# ---------------- AI QUOTE ----------------

def get_ai_quote():
    try:
        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {"inputs": "Generate one short motivational quote for job seekers."}

        res = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )

        result = res.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].strip()

    except Exception as e:
        print("Quote error:", e)

    return "Success is built one application at a time."

# ---------------- SCRAPERS ----------------

def get_infopark_jobs():
    soup = fetch("https://infopark.in/companies/job-search")
    jobs = []

    for a in soup.select("a"):
        href = a.get("href", "")
        text = clean(a.get_text())

        if "/company/" in href and "/job/" in href and len(text) > 10:
            jobs.append({
                "title": text,
                "company": "Infopark Company",
                "link": "https://infopark.in" + href
            })
    return jobs

def get_technopark_jobs():
    soup = fetch("https://technopark.in/job-search")
    jobs = []

    for a in soup.select("a"):
        href = a.get("href", "")
        text = clean(a.get_text())

        if "/job/" in href and len(text) > 10:
            jobs.append({
                "title": text,
                "company": "Technopark Company",
                "link": "https://technopark.in" + href
            })
    return jobs

def get_cyberpark_jobs():
    soup = fetch("https://www.ulcyberpark.com/jobs")
    jobs = []

    for tag in soup.select("a"):
        href = tag.get("href", "")
        text = clean(tag.get_text())

        if "job" in text.lower() and len(text) > 12:
            link = href if href.startswith("http") else "https://www.ulcyberpark.com" + href
            jobs.append({
                "title": text,
                "company": "Cyberpark Company",
                "link": link
            })
    return jobs

# ---------------- MAILER ----------------

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"

    quote = get_ai_quote()
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

# ---------------- MAIN ----------------

if __name__ == "__main__":
    jobs = []
    jobs += get_infopark_jobs()
    jobs += get_technopark_jobs()
    jobs += get_cyberpark_jobs()

    print("Total jobs collected:", len(jobs))
    send_email(jobs)
