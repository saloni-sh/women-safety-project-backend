import numpy as np
import sounddevice as sd
import librosa
from tensorflow.keras.models import load_model
import joblib
import threading, time
from difflib import SequenceMatcher

# ---------------- GLOBAL VARIABLES ---------------- #
model = None
label_encoder = None
trigger_detected = False
last_trigger_time = 0  # for cooldown handling

# ---------------- CONFIGURABLE PARAMETERS ---------------- #
TRIGGER_WORDS = ["madat_karo", "mujhe_bachao","help_me","save_me","i_need_help"]  # ✅ exact triggers
CONFIDENCE_THRESHOLD = 0.90  # must be very confident
LISTEN_DURATION = 3          # seconds
LISTEN_COOLDOWN = 2          # seconds pause after each listen cycle
GAIN = 3.0                   # Audio amplification factor (2.0–5.0)
SILENCE_THRESHOLD = 0.005    # Detects if user’s voice is too quiet
COOLDOWN_SECONDS = 10        # Prevent retriggering quickly
ALLOW_FUZZY_MATCH = True     # optional — allow minor variations like "mujhebachao"

# ---------------- MODEL LOADING ---------------- #
def load_voice_model():
    """Load the model and label encoder only once."""
    global model, label_encoder
    if model is None or label_encoder is None:
        print("🧠 Loading voice model...")
        try:
            model = load_model("model/voice_model.h5")
            label_encoder = joblib.load("model/label_encoder.pkl")
            print("✅ Voice model loaded successfully.")
        except Exception as e:
            print(f"❌ Error loading model: {e}")


# ---------------- FEATURE EXTRACTION ---------------- #
def extract_features(audio, sr, max_pad_len=50):
    """Extract MFCC features from audio."""
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    pad_width = max_pad_len - mfcc.shape[1]
    if pad_width > 0:
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :max_pad_len]
    return mfcc


# ---------------- FUZZY MATCHING ---------------- #
def is_similar(a, b, threshold=0.85):
    """Check if two words are similar enough."""
    return SequenceMatcher(None, a, b).ratio() >= threshold


# ---------------- PROCESS PREDICTION ---------------- #
def process_prediction(pred_label, confidence):
    """Validate prediction with strict trigger and confidence checks."""
    global last_trigger_time

    current_time = time.time()
    normalized_label = pred_label.lower().replace(" ", "_")

    # ⏳ Prevent repeated triggers within cooldown time
    if current_time - last_trigger_time < COOLDOWN_SECONDS:
        print("⏳ Cooldown active — ignoring detection.")
        return False

    # 🎯 Exact match or fuzzy match if enabled
    for trigger in TRIGGER_WORDS:
        if (
            (normalized_label == trigger or
             (ALLOW_FUZZY_MATCH and is_similar(normalized_label, trigger)))
            and confidence >= CONFIDENCE_THRESHOLD
        ):
            print(f"🚨 Valid trigger detected: {normalized_label} (confidence: {confidence:.2f})")
            last_trigger_time = current_time
            return True

    print(f"🟢 Ignored: {normalized_label} (confidence: {confidence:.2f}) — not a valid trigger.")
    return False


# ---------------- LISTENING FUNCTION ---------------- #
def listen(duration=LISTEN_DURATION, fs=44100):
    """Listen to mic input and detect emergency trigger words."""
    global trigger_detected
    load_voice_model()

    print("🎙 Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    audio = audio.flatten()

    # 🧠 Amplify audio
    audio = np.clip(audio * GAIN, -1.0, 1.0)

    # 🔇 Ignore silent or background noise
    rms = np.sqrt(np.mean(audio ** 2))
    if rms < SILENCE_THRESHOLD:
        print("🔇 Low audio detected — ignoring background noise.")
        return

    # 🎵 Extract MFCC features
    features = extract_features(audio, fs)
    X = np.expand_dims(features, axis=(0, -1))

    # 🤖 Predict voice command
    preds = model.predict(X)
    confidence = float(np.max(preds))
    pred_label = label_encoder.inverse_transform([np.argmax(preds)])[0]
    print(f"Detected: {pred_label} (confidence: {confidence:.2f})")

    # 🚨 Strict trigger validation
    if process_prediction(pred_label, confidence):
        trigger_detected = True
    else:
        print("🟢 No valid trigger detected.")

    time.sleep(LISTEN_COOLDOWN)


# ---------------- BACKGROUND LISTENER LOOP ---------------- #
def start_listening_background():
    """Run the voice listener continuously in a separate thread."""
    def loop():
        global trigger_detected
        while True:
            if not trigger_detected:
                try:
                    listen()
                except Exception as e:
                    print(f"⚠ Voice listening error: {e}")
                    time.sleep(2)
            else:
                print("🚨 Trigger detected — pausing listening loop for 5 seconds.")
                time.sleep(5)
    threading.Thread(target=loop, daemon=True).start()


# ---------------- TRIGGER UTILITIES ---------------- #
def is_triggered():
    """Check if a trigger was detected."""
    return trigger_detected


def reset_trigger():
    """Reset the trigger flag."""
    global trigger_detected
    trigger_detected = False