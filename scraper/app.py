import os
import smtplib

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

print("EMAIL_USER:", EMAIL_USER)
print("EMAIL_TO:", EMAIL_TO)

msg = "Subject: Test Mail from GitHub Action\n\nThis is a test email."

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL_USER, EMAIL_PASS)
server.sendmail(EMAIL_USER, EMAIL_TO, msg)
server.quit()

print("MAIL SENT")
