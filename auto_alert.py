from speech_recognition_module import listen_for_trigger
from gps_module import get_location
from voice_record import record_audio
from mailer import send_email
import time

print("🟢 Voice-activated emergency alert system started...")

while True:
    # Listen for trigger phrase ("help me", "save me", etc.)
    triggered = listen_for_trigger()

    if triggered:
        print("🚨 Emergency Trigger Detected!")

        # 1️⃣ Record emergency audio
        audio_file = record_audio(duration=10)

        # 2️⃣ Get user location
        lat, lon, map_link = get_location()

        # 3️⃣ Send alert email
        notes = "Emergency triggered via voice."
        send_email(lat, lon, notes, map_link, audio_file)

        print("✅ Alert sent successfully!")

        # Optional delay to prevent repeated alerts
        print("⏱ Waiting 30 seconds before next detection...")
        time.sleep(30)

    else:
        print("🎧 Listening for voice trigger...")
        time.sleep(2)
