import requests
from bs4 import BeautifulSoup
import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# -------------------- INFOPARK --------------------

def infopark_jobs():
    url = "https://infopark.in/companies/job-search"
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
    jobs = []

    for card in soup.select("div.job-listing"):
        title = card.select_one("h4")
        company = card.select_one("p.company")
        link = card.find("a")

        if title and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip() if company else "Infopark Company",
                "link": "https://infopark.in" + link["href"]
            })
    return jobs

# -------------------- TECHNOPARK --------------------

def technopark_jobs():
    url = "https://technopark.in/job-search"
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
    jobs = []

    for card in soup.select("div.job-card"):
        title = card.select_one("h3")
        company = card.select_one("span.company")
        link = card.find("a")

        if title and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip() if company else "Technopark Company",
                "link": "https://technopark.in" + link["href"]
            })
    return jobs

# -------------------- CYBERPARK --------------------

def cyberpark_jobs():
    url = "https://www.ulcyberpark.com/jobs"
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
    jobs = []

    for card in soup.select("div.job-box"):
        title = card.select_one("h4")
        company = card.select_one("span.company")
        link = card.find("a")

        if title and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip() if company else "Cyberpark Company",
                "link": link["href"]
            })
    return jobs

# -------------------- EMAIL --------------------

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"
    body = ""

    if not jobs:
        body = "No jobs found today."
    else:
        for j in jobs:
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

    print("Sent", len(jobs), "jobs")

# -------------------- MAIN --------------------

if __name__ == "__main__":
    jobs = []
    jobs += infopark_jobs()
    jobs += technopark_jobs()
    jobs += cyberpark_jobs()

    print("Collected:", len(jobs))
    send_email(jobs)
