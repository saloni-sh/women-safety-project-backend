import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(filename="emergency_audio.wav", duration=10, fs=44100):
    """
    Record audio from the microphone for a given duration and save it as a WAV file.

    Parameters:
        filename (str): Output filename (default: emergency_audio.wav)
        duration (int): Recording duration in seconds
        fs (int): Sampling rate (default: 44100 Hz)

    Returns:
        str: Path to the saved audio file
    """
    try:
        print(f"🎤 Recording for {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        write(filename, fs, recording)
        print(f"✅ Audio saved: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error recording audio: {e}")
        return None
