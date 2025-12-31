import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib, os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HEADERS = {"User-Agent": "Mozilla/5.0"}

REGIONS = [
    ("Kerala", "Kochi"),
    ("Kerala", "Trivandrum"),
    ("Tamil Nadu", "Chennai"),
    ("Tamil Nadu", "Coimbatore"),
    ("Karnataka", "Bangalore"),
]

def scrape_indeed(city):
    jobs = []
    url = f"https://in.indeed.com/jobs?q=software+developer&l={city}"
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
    for card in soup.select("div.job_seen_beacon")[:8]:
        title = card.select_one("h2").get_text(strip=True)
        company = card.select_one(".companyName").get_text(strip=True)
        link = "https://in.indeed.com" + card.select_one("a")["href"]
        jobs.append((title, company, link))
    return jobs

def scrape_google(city):
    jobs = []
    q = f"software developer jobs in {city}"
    url = f"https://www.google.com/search?q={q}"
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
    for g in soup.select("div.g")[:6]:
        if g.h3 and g.a:
            jobs.append((g.h3.text, "Company", g.a["href"]))
    return jobs

def get_jobs():
    all_jobs = []
    for state, city in REGIONS:
        all_jobs += scrape_indeed(city)
        all_jobs += scrape_google(city)
    return all_jobs

def send_email(jobs):
    subject = f"South India IT Jobs — {datetime.now().strftime('%d %b %Y')}"
    body = ""
    for t, c, l in jobs[:40]:
        body += f"{t}\n{c}\n{l}\n\n"
    if not body:
        body = "No jobs found today."

    msg = f"Subject: {subject}\n\n{body}"
    with smtplib.SMTP("smtp.gmail.com",587) as s:
        s.starttls()
        s.login(EMAIL_USER, EMAIL_PASS)
        s.sendmail(EMAIL_USER, EMAIL_TO, msg)

if __name__ == "__main__":
    jobs = get_jobs()
    print("Jobs found:", len(jobs))
    send_email(jobs)
