import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read credentials and contacts from .env
EMAIL = os.getenv("ALERT_EMAIL")
PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")
TRUSTED_CONTACTS = [c.strip() for c in os.getenv("TRUSTED_CONTACTS", "").split(",") if c.strip()]

def send_email(latitude, longitude, notes="", map_link=None, audio_file=None):
    """
    Send emergency alert email with:
    - GPS location (latitude & longitude)
    - Google Maps link
    - Optional notes
    - Optional audio attachment (.wav)
    """

    if not EMAIL or not PASSWORD or not TRUSTED_CONTACTS:
        print("❌ Missing email credentials or contacts in .env file.")
        return

    try:
        # Create email message
        msg = EmailMessage()
        msg["From"] = EMAIL
        msg["To"] = ", ".join(TRUSTED_CONTACTS)
        msg["Subject"] = "🚨 Emergency Alert"

        # Message body
        body = f"⚠️ Emergency triggered!\n\n"
        body += f"📍 Location: {latitude}, {longitude}\n"
        if map_link:
            body += f"🗺️ Google Maps: {map_link}\n"
        if notes:
            body += f"\n📝 Notes: {notes}\n"

        msg.set_content(body)

        # Attach audio if provided
        if audio_file and os.path.exists(audio_file):
            try:
                with open(audio_file, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype="audio",
                        subtype="wav",
                        filename=os.path.basename(audio_file)
                    )
                print(f"🎧 Attached audio file: {audio_file}")
            except Exception as e:
                print(f"❌ Failed to attach audio file: {e}")
        else:
            print("⚠️ No audio file attached or file not found.")

        # Send the email using Gmail SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        print("✅ Emergency alert email sent successfully!")

    except Exception as e:
        print(f"❌ Error while sending email: {e}")  