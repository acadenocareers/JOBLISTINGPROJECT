import json, os, smtplib, random
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ---------- ENV VARIABLES ----------
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")
USER_NAME  = os.getenv("USER_NAME", "Student")

if not EMAIL_USER or not EMAIL_PASS or not EMAIL_TO:
    raise Exception("Missing email environment variables")

# ---------- LOAD RANDOM QUOTE ----------
quotes_df = pd.read_excel("scraper/career_quotes_unique.xlsx")
quote = random.choice(quotes_df["Quote"].dropna().tolist())

# ---------- LOAD JOBS ----------
with open("scraper/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

today = datetime.now().strftime("%d %B %Y")

# ---------- JOB CARDS ----------
cards = ""

sampled_jobs = random.sample(jobs, min(20, len(jobs)))

for job in sampled_jobs:

    raw_link = job.get("link", "").strip()

    if not raw_link.startswith("http"):
        raw_link = "https://" + raw_link

    raw_link = raw_link.replace("infopark.inhttps://", "https://infopark.in/")
    link = raw_link

    cards += f"""
    <div style="border:1px solid #e6e9f0;border-radius:14px;padding:22px;
                margin:18px 0;background:#fafbff">

        <h3 style="color:#5f2cff;margin:0 0 8px 0;font-size:18px">
            {job.get('title','')}
        </h3>

        <a href="{link}" target="_blank"
           style="
           display:inline-block;
           margin-top:10px;
           padding:10px 22px;
           background:linear-gradient(90deg,#5f2cff,#ff7a18);
           color:#ffffff;
           text-decoration:none;
           font-weight:600;
           font-size:14px;
           letter-spacing:0.3px;
           border-radius:10px;
           box-shadow:0 6px 14px rgba(95,44,255,0.35);
           ">
           View & Apply
        </a>
    </div>
    """

# ---------- HTML EMAIL ----------
html = f"""
<html>
<body style="font-family:'Segoe UI',Arial;background:#f4f6fb;padding:30px">

<div style="max-width:760px;margin:auto;background:white;border-radius:18px;
            box-shadow:0 10px 25px rgba(0,0,0,0.08);overflow:hidden">

<div style="background:linear-gradient(135deg,#5f2cff,#ff7a18);
            padding:32px;color:white;text-align:center">

<img src="https://drive.google.com/uc?export=view&id=1a31PXpN-FMK5lq8JJt-OPBJz6IEO7ZvC"
     width="90" style="display:block;margin:0 auto 10px;">

<h1 style="margin:0;font-size:28px;">Acadeno Technologies</h1>
<p style="margin:6px 0 0;font-size:14px;opacity:0.9">Verified IT Opportunities</p>
</div>

<div style="padding:32px">

<p style="font-size:15px;">Dear <b>{USER_NAME}</b>,</p>

<p style="font-style:italic;color:#444;">“{quote}”</p>

<p style="font-weight:600;margin-top:20px;">Here are today’s opportunities — <b>{today}</b></p>

{cards}

<p style="margin-top:28px;font-size:14px;color:#666">
Your future is not waiting to happen — it’s waiting for you to make it happen ✨
</p>

<p style="font-size:14px;color:#666">— Team Acadeno</p>
</div>

<div style="background:#f1f3f8;padding:20px;text-align:center;font-size:13px;color:#666">
© {datetime.now().year} Acadeno Technologies • Building AI Careers
</div>

</div>
</body>
</html>
"""

# ---------- SEND EMAIL ----------
msg = MIMEMultipart("alternative")
msg["Subject"] = f"Today's Verified IT Openings — {today}"
msg["From"] = EMAIL_USER
msg["To"] = EMAIL_TO
msg.attach(MIMEText(html, "html"))

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL_USER, EMAIL_PASS)
server.send_message(msg)
server.quit()

print("Email sent successfully")
