# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# import os
# import socket
# import time
# import threading
# from flask import Flask, render_template, request, jsonify
# from database import db, Alert
# from speech_recognition_module import start_listening_background, is_triggered, reset_trigger
# from gps_module import get_location
# from voice_record import record_audio
# from mailer import send_email
# from flask import Flask, render_template, request, redirect, url_for, flash, session
# from flask_mysqldb import MySQL
# from flask_bcrypt import Bcrypt

# # Suppress TensorFlow logs
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# # ---------------- FLASK APP INITIALIZATION ---------------- #
# app = Flask(__name__)

# # ---------------- DATABASE CONFIGURATION ---------------- #
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alerts.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

# # Create database tables (if not exists)
# with app.app_context():
#     db.create_all()

# # ---------------- GLOBAL VARIABLES ---------------- #
# ALERT_COOLDOWN = 30  # seconds
# last_alert_time = 0


# # ---------------- ROUTES ---------------- #
# # @app.route('/')
# # def home():
# #     """Main route (optional frontend)."""
# #     return render_template('register.html')


# app = Flask(__name__)
# app.secret_key = "your_secret_key"

# @app.route('/')
# def home():
#     return redirect(url_for('register'))


# # MySQL Config
# # app.config['MYSQL_USER'] = 'root'
# # app.config['MYSQL_PASSWORD'] = '12345'
# app.config['MYSQL_DB'] = 'flask_auth'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'flaskuser'
# app.config['MYSQL_PASSWORD'] = 'flaskpass'


# mysql = MySQL(app)
# bcrypt = Bcrypt(app)

# # Register Route
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO users(username, email, password) VALUES(%s, %s, %s)", (username, email, password))
#         mysql.connection.commit()
#         cur.close()
#         flash("Registration successful! Please login.", "success")
#         return redirect(url_for('login'))
#     return render_template('register.html')

# # Login Route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password_candidate = request.form['password']

#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM users WHERE email=%s", [email])
#         user = cur.fetchone()
#         cur.close()

#         if user and bcrypt.check_password_hash(user[3], password_candidate):
#             session['logged_in'] = True
#             session['username'] = user[1]
#             flash("Login successful!", "success")
#             return redirect(url_for('dashboard'))
#         else:
#             flash("Invalid credentials!", "danger")
#     return render_template('login.html')

# # Dashboard (Protected Route)
# @app.route('/dashboard')
# def dashboard():
#     if 'logged_in' in session:
#         return render_template('dashboard.html', username=session['username'])
#     flash("You need to login first!", "warning")
#     return redirect(url_for('login'))

# # Logout Route
# @app.route('/logout')
# def logout():
#     session.clear()
#     flash("You have been logged out.", "info")
#     return redirect(url_for('login'))

# # ____________________________________________________________________


# @app.route('/alert', methods=['POST'])
# def alert():
#     """
#     Manual alert from frontend (via POST request).
#     Saves alert to database and sends email with location & audio.
#     """
#     data = request.json or {}
#     notes = data.get("notes", "")

#     # Get location
#     lat, lon, map_link = get_location()

#     # Record short audio
#     audio_file = record_audio(duration=10)

#     # Save alert in database
#     new_alert = Alert(latitude=lat, longitude=lon, notes=notes)
#     db.session.add(new_alert)
#     db.session.commit()

#     # Send email
#     send_email(lat, lon, notes, map_link, audio_file)

#     return jsonify({"status": "success", "message": "Alert sent successfully!"})


# @app.route('/get_location')
# def get_gps():
#     """Returns current location and Google Maps link."""
#     lat, lon, map_link = get_location()
#     return jsonify({"latitude": lat, "longitude": lon, "map_link": map_link})


# # ---------------- BACKGROUND VOICE MONITOR ---------------- #
# def check_trigger_loop():
#     """Continuously checks for emergency trigger phrases."""
#     global last_alert_time
#     while True:
#         try:
#             if is_triggered():
#                 current_time = time.time()
#                 if current_time - last_alert_time < ALERT_COOLDOWN:
#                     print("⏳ Cooldown active — skipping repeated alert.")
#                 else:
#                     last_alert_time = current_time
#                     print("🚨 Emergency Trigger Detected! Sending alert...")

#                     # Record audio evidence
#                     audio_file = record_audio(duration=10)

#                     # Get location
#                     lat, lon, map_link = get_location()
#                     notes = "Emergency triggered via voice"

#                     # Save to DB
#                     with app.app_context():
#                         new_alert = Alert(latitude=lat, longitude=lon, notes=notes)
#                         db.session.add(new_alert)
#                         db.session.commit()

#                     # Send email alert
#                     send_email(lat, lon, notes, map_link, audio_file)

#                 # Reset trigger flag after handling
#                 reset_trigger()

#         except Exception as e:
#             print(f"⚠ Voice monitor error: {e}")

#         time.sleep(1)


# # ---------------- MAIN ENTRY POINT ---------------- #
# if __name__ == '__main__':
#     print("🎤 Starting background voice listener...")

#     # Start background threads only once
#     threading.Thread(target=start_listening_background, daemon=True).start()
#     threading.Thread(target=check_trigger_loop, daemon=True).start()

#     print("👂 Voice trigger monitoring active...")

#     # Get local network IP for showing URL
#     hostname = socket.gethostname()
#     local_ip = socket.gethostbyname(hostname)

#     print("\n🚀 Flask app running at:")
#     print(f"➡ Local:    http://127.0.0.1:5000")
#     print(f"➡ Network:  http://{local_ip}:5000\n")

#     # ✅ Disable reloader to prevent duplicate threads
#     app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)


# _________________________________________________________________________________________________________

import os
import socket
import time
import threading

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash, session
)
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

from database import db, Alert
from speech_recognition_module import start_listening_background, is_triggered, reset_trigger
from gps_module import get_location
from voice_record import record_audio
from mailer import send_email

# Suppress TensorFlow logs early
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ---------------- FLASK APP INITIALIZATION ---------------- #
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change to a strong random value in production

# ---------------- SQLALCHEMY (SQLite) CONFIG ---------------- #
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create SQLite tables (if not exists)
with app.app_context():
    db.create_all()

# ---------------- MySQL CONFIG (Auth) ---------------- #
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'flaskuser'
app.config['MYSQL_PASSWORD'] = 'flaskpass'
app.config['MYSQL_DB'] = 'flask_auth'
# Optional: set to True if you use dict-style results
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# ---------------- GLOBALS ---------------- #
ALERT_COOLDOWN = 30  # seconds
last_alert_time = 0

# ---------------- ROUTES ---------------- #
@app.route('/')
def home():
    # Redirect to register page
    return redirect(url_for('register'))

# Register Route (with duplicate checks + graceful error handling)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        raw_password = request.form['password']

        # Basic server-side validation
        if not username or not email or not raw_password:
            flash("All fields are required.", "danger")
            return redirect(url_for('register'))

        password_hash = bcrypt.generate_password_hash(raw_password).decode('utf-8')

        try:
            cur = mysql.connection.cursor()

            # Check existing username
            cur.execute("SELECT id FROM users WHERE username=%s", [username])
            existing_username = cur.fetchone()

            if existing_username:
                cur.close()
                flash("Username already taken. Please choose another.", "danger")
                return redirect(url_for('register'))

            # Check existing email
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE email=%s", [email])
            existing_email = cur.fetchone()

            if existing_email:
                cur.close()
                flash("Email already registered. Try logging in.", "warning")
                return redirect(url_for('login'))

            # Insert new user
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO users(username, email, password) VALUES(%s, %s, %s)",
                (username, email, password_hash)
            )
            mysql.connection.commit()
            cur.close()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            # Log the actual error to console for debugging
            print(f"⚠ Register error: {e}")
            flash("Registration failed due to a server error.", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password_candidate = request.form['password']

        if not email or not password_candidate:
            flash("Email and password are required.", "danger")
            return redirect(url_for('login'))

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s", [email])
            user = cur.fetchone()
            cur.close()

            # Assuming users table columns: id(0), username(1), email(2), password(3)
            if user and bcrypt.check_password_hash(user[3], password_candidate):
                session['logged_in'] = True
                session['username'] = user[1]
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials!", "danger")
                return redirect(url_for('login'))

        except Exception as e:
            print(f"⚠ Login error: {e}")
            flash("Login failed due to a server error.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard (Protected)
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        return render_template('dashboard.html', username=session['username'])
    flash("You need to login first!", "warning")
    return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Alert API (uses SQLite via SQLAlchemy)
@app.route('/alert', methods=['POST'])
def alert():
    try:
        data = request.json or {}
        notes = data.get("notes", "").strip()

        # Location
        lat, lon, map_link = get_location()

        # Audio
        audio_file = record_audio(duration=10)

        # Save alert
        new_alert = Alert(latitude=lat, longitude=lon, notes=notes)
        db.session.add(new_alert)
        db.session.commit()

        # Send email
        send_email(lat, lon, notes, map_link, audio_file)

        return jsonify({"status": "success", "message": "Alert sent successfully!"})

    except Exception as e:
        print(f"⚠ Alert route error: {e}")
        return jsonify({"status": "error", "message": "Failed to send alert"}), 500

# GPS API
@app.route('/get_location')
def get_gps():
    try:
        lat, lon, map_link = get_location()
        return jsonify({"latitude": lat, "longitude": lon, "map_link": map_link})
    except Exception as e:
        print(f"⚠ GPS route error: {e}")
        return jsonify({"error": "Failed to get location"}), 500

# ---------------- BACKGROUND VOICE MONITOR ---------------- #
def check_trigger_loop():
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

                    audio_file = record_audio(duration=10)
                    lat, lon, map_link = get_location()
                    notes = "Emergency triggered via voice"

                    # Use app context when touching SQLAlchemy
                    with app.app_context():
                        new_alert = Alert(latitude=lat, longitude=lon, notes=notes)
                        db.session.add(new_alert)
                        db.session.commit()

                    send_email(lat, lon, notes, map_link, audio_file)

                reset_trigger()
        except Exception as e:
            print(f"⚠ Voice monitor error: {e}")
        time.sleep(1)

# ---------------- ERROR HANDLERS (Optional but helpful) ---------------- #
@app.errorhandler(500)
def internal_error(_error):
    # Show a friendly message instead of crashing silently
    flash("Internal server error occurred.", "danger")
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(_error):
    flash("Page not found.", "warning")
    return redirect(url_for('home'))

# ---------------- MAIN ENTRY ---------------- #
if __name__ == '__main__':
    print("🎤 Starting background voice listener...")
    threading.Thread(target=start_listening_background, daemon=True).start()
    threading.Thread(target=check_trigger_loop, daemon=True).start()
    print("👂 Voice trigger monitoring active...")

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print("\n🚀 Flask app running at:")
    print(f"➡ Local:    http://127.0.0.1:5000")
    print(f"➡ Network:  http://{local_ip}:5000\n")

    # Disable reloader to avoid duplicate threads
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
