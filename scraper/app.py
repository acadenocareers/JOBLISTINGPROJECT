import requests
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ---------------------------
# SAFE JSON FETCH
# ---------------------------
def safe_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"⚠️ Failed to load {url} -> {e}")
        return None

# ---------------------------
# TECHNOPARK
# ---------------------------
def get_technopark_jobs():
    url = "https://www.technopark.org/api/jobs"
    data = safe_json(url)
    jobs = []

    if not isinstance(data, list):
        return jobs

    for j in data:
        title = j.get("title", "Unknown Role")
        company = j.get("company", "Unknown Company")
        link = j.get("url", "")
        jobs.append(f"{title} | {company} | Technopark\n{link}")

    return jobs

# ---------------------------
# INFOPARK
# ---------------------------
def get_infopark_jobs():
    url = "https://infopark.in/api/job/list"
    data = safe_json(url)
    jobs = []

    if not data or "jobs" not in data:
        return jobs

    for j in data["jobs"]:
        title = j.get("title", "Unknown Role")
        company = j.get("company", "Unknown Company")
        link = j.get("link", "")
        jobs.append(f"{title} | {company} | Infopark\n{link}")

    return jobs

# ---------------------------
# CYBERPARK
# ---------------------------
def get_cyberpark_jobs():
    url = "https://www.cyberparkkerala.org/api/jobs"
    data = safe_json(url)
    jobs = []

    if not isinstance(data, list):
        return jobs

    for j in data:
        title = j.get("title", "Unknown Role")
        company = j.get("company", "Unknown Company")
        link = j.get("apply_link", "")
        jobs.append(f"{title} | {company} | Cyberpark\n{link}")

    return jobs

# ---------------------------
# EMAIL
# ---------------------------
def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"
    body = "\n\n".join(jobs) if jobs else "No jobs found today."

    msg = MIMEText(body)
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("📧 Mail sent")

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    print("🚀 Collecting Kerala IT jobs...")

    all_jobs = []
    all_jobs.extend(get_technopark_jobs())
    all_jobs.extend(get_infopark_jobs())
    all_jobs.extend(get_cyberpark_jobs())

    print(f"✅ Total jobs collected: {len(all_jobs)}")

    send_email(all_jobs)
