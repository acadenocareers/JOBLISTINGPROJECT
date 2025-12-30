import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------- SCRAPERS ----------------

def get_infopark_jobs():
    url = "https://infopark.in/companies/job-search"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    jobs = []
    for card in soup.select(".company-list .company-list-item"):
        title = card.select_one("h3")
        company = card.select_one(".company-title")
        link = card.select_one("a")

        if title and company and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip(),
                "link": "https://infopark.in" + link["href"]
            })
    return jobs


def get_technopark_jobs():
    url = "https://technopark.in/job-search"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    jobs = []
    for card in soup.select(".job-listing"):
        title = card.select_one("h3")
        company = card.select_one(".company")
        link = card.select_one("a")

        if title and company and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip(),
                "link": "https://technopark.in" + link["href"]
            })
    return jobs


def get_cyberpark_jobs():
    url = "https://www.ulcyberpark.com/jobs"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    jobs = []
    for card in soup.select(".job-list"):
        title = card.select_one("h4")
        company = card.select_one("p")
        link = card.select_one("a")

        if title and company and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip(),
                "link": link["href"]
            })
    return jobs


# ---------------- MAILER ----------------

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"
    body = ""

    if not jobs:
        body = "No jobs found today."
    else:
        for j in jobs:
            body += f"{j['title']} | {j['company']}\n{j['link']}\n\n"

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


# ---------------- MAIN ----------------

if __name__ == "__main__":
    print("Collecting Kerala IT jobs...")

    jobs = []
    jobs += get_infopark_jobs()
    jobs += get_technopark_jobs()
    jobs += get_cyberpark_jobs()

    print(f"Total jobs found: {len(jobs)}")
    send_email(jobs)
