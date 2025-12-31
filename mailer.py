import json, os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

if not EMAIL_USER or not EMAIL_PASS or not EMAIL_TO:
    raise Exception("Missing email environment variables")

# Load jobs
with open("scraper/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

today = datetime.now().strftime("%d %B %Y")

# ---------- Job Cards ----------
cards = ""
for job in jobs[:20]:
    cards += f"""
    <div style="background:#ffffff;border-radius:12px;padding:18px;margin-bottom:15px;
                box-shadow:0 4px 10px rgba(0,0,0,0.08)">
        <h3 style="color:#5b2dff;margin-bottom:6px">{job['title']}</h3>
        <p style="margin:4px 0"><b>🏢 {job['company']}</b></p>
        <p style="margin:4px 0;color:#555">📍 {job['park']}</p>
        <a href="{job.get('link','')}" 
           style="display:inline-block;margin-top:8px;padding:10px 16px;
                  background:linear-gradient(90deg,#ff7a18,#ff3d77);
                  color:white;text-decoration:none;border-radius:8px;font-weight:bold">
           🔗 View & Apply
        </a>
    </div>
    """

# ---------- HTML Email ----------
html = f"""
<html>
<body style="font-family:Segoe UI,Arial;background:#f2f3f7;padding:25px">
<div style="max-width:700px;margin:auto">

<!-- PROFESSIONAL HEADER -->
<div style="background:linear-gradient(90deg,#6a11cb,#ff5f00);
            padding:28px;border-radius:16px;color:white;text-align:center">

<img src="https://drive.google.com/uc?export=view&id=1a31PXpN-FMK5lq8JJt-OPBJz6IEO7ZvC"
     alt="Acadeno Logo"
     width="120"
     style="display:block;margin:0 auto 6px;">

<h1 style="margin:6px 0 2px 0;font-size:28px;font-weight:700;">
Acadeno Technologies Private Limited
</h1>

<p style="margin:0;font-size:14px;opacity:0.9;">
Where AI Builds Careers
</p>
</div>

<!-- CONTENT -->
<div style="background:white;margin-top:22px;padding:30px;border-radius:16px">
<p>Dear <b>Aswathy</b>,</p>

<p>
Every great career begins with a single step — a moment of courage, determination,
and belief in yourself 🌱
</p>

<p><b>Here are today’s verified Kerala IT opportunities ({today}):</b></p>

{cards}

<p style="margin-top:30px;font-size:14px;color:#666">
Your future is not waiting to happen — it’s waiting for you to make it happen ✨
</p>

<p style="font-size:14px;color:#666">— Team Acadeno</p>
</div>
</div>
</body>
</html>
"""

# ---------- Send Mail ----------
msg = MIMEMultipart("alternative")
msg["Subject"] = f"Today's Verified Kerala IT Openings — {today}"
msg["From"] = EMAIL_USER
msg["To"] = EMAIL_TO
msg.attach(MIMEText(html, "html"))

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL_USER, EMAIL_PASS)
server.send_message(msg)
server.quit()

print("Email sent successfully")
