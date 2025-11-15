from flask import Flask
import tensorflow as tf

print("✅ TensorFlow loaded successfully:", tf.__version__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask working fine ✅"

if __name__ == '__main__':
    print("🚀 Running test Flask app...")
    app.run(debug=True)
