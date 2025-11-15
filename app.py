import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import os
import socket
import time
import threading
from flask import Flask, render_template, request, jsonify
from database import db, Alert
from speech_recognition_module import start_listening_background, is_triggered, reset_trigger
from gps_module import get_location
from voice_record import record_audio
from mailer import send_email

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ---------------- FLASK APP INITIALIZATION ---------------- #
app = Flask(__name__)

# ---------------- DATABASE CONFIGURATION ---------------- #
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables (if not exists)
with app.app_context():
    db.create_all()

# ---------------- GLOBAL VARIABLES ---------------- #
ALERT_COOLDOWN = 30  # seconds
last_alert_time = 0


# ---------------- ROUTES ---------------- #
@app.route('/')
def home():
    """Main route (optional frontend)."""
    return render_template('index.html')


@app.route('/alert', methods=['POST'])
def alert():
    """
    Manual alert from frontend (via POST request).
    Saves alert to database and sends email with location & audio.
    """
    data = request.json or {}
    notes = data.get("notes", "")

    # Get location
    lat, lon, map_link = get_location()

    # Record short audio
    audio_file = record_audio(duration=10)

    # Save alert in database
    new_alert = Alert(latitude=lat, longitude=lon, notes=notes)
    db.session.add(new_alert)
    db.session.commit()

    # Send email
    send_email(lat, lon, notes, map_link, audio_file)

    return jsonify({"status": "success", "message": "Alert sent successfully!"})


@app.route('/get_location')
def get_gps():
    """Returns current location and Google Maps link."""
    lat, lon, map_link = get_location()
    return jsonify({"latitude": lat, "longitude": lon, "map_link": map_link})


# ---------------- BACKGROUND VOICE MONITOR ---------------- #
def check_trigger_loop():
    """Continuously checks for emergency trigger phrases."""
    global last_alert_time
    while True:
        try:
            if is_triggered():
                current_time = time.time()
                if current_time - last_alert_time < ALERT_COOLDOWN:
                    print("⏳ Cooldown active — skipping repeated alert.")
                else:
                    last_alert_time = current_time
                    print("🚨 Emergency Trigger Detected! Sending alert...")

                    # Record audio evidence
                    audio_file = record_audio(duration=10)

                    # Get location
                    lat, lon, map_link = get_location()
                    notes = "Emergency triggered via voice"

                    # Save to DB
                    with app.app_context():
                        new_alert = Alert(latitude=lat, longitude=lon, notes=notes)
                        db.session.add(new_alert)
                        db.session.commit()

                    # Send email alert
                    send_email(lat, lon, notes, map_link, audio_file)

                # Reset trigger flag after handling
                reset_trigger()

        except Exception as e:
            print(f"⚠ Voice monitor error: {e}")

        time.sleep(1)


# ---------------- MAIN ENTRY POINT ---------------- #
if __name__ == '__main__':
    print("🎤 Starting background voice listener...")

    # Start background threads only once
    threading.Thread(target=start_listening_background, daemon=True).start()
    threading.Thread(target=check_trigger_loop, daemon=True).start()

    print("👂 Voice trigger monitoring active...")

    # Get local network IP for showing URL
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print("\n🚀 Flask app running at:")
    print(f"➡ Local:    http://127.0.0.1:5000")
    print(f"➡ Network:  http://{local_ip}:5000\n")

    # ✅ Disable reloader to prevent duplicate threads
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
