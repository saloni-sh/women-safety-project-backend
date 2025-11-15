import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load .env file
load_dotenv()

ALERT_EMAIL = os.getenv("ALERT_EMAIL")
ALERT_EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")
TRUSTED_CONTACTS = os.getenv("TRUSTED_CONTACTS").split(",")

def test_send_email():
    try:
        # Email content
        subject = "✅ Test Email from Safety App"
        body = "This is a test email to check Gmail SMTP with App Password."
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = ALERT_EMAIL
        msg["To"] = ", ".join(TRUSTED_CONTACTS)

        # Connect to Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(ALERT_EMAIL, ALERT_EMAIL_PASSWORD)
        server.sendmail(ALERT_EMAIL, TRUSTED_CONTACTS, msg.as_string())
        server.quit()

        print("✅ Test email sent successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_send_email()
