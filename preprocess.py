# preprocess.py
import os
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
import joblib

def extract_features(file_path, max_pad_len=50):
    try:
        audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
        mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        pad_width = max_pad_len - mfcc.shape[1]
        if pad_width > 0:
            mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
        else:
            mfcc = mfcc[:, :max_pad_len]
        return mfcc
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def load_data(dataset_path="dataset"):
    labels = []
    features = []

    for label in os.listdir(dataset_path):
        folder = os.path.join(dataset_path, label)
        if not os.path.isdir(folder):
            continue

        print(f"🔍 Loading: {label}")
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                file_path = os.path.join(folder, file)
                mfcc = extract_features(file_path)
                if mfcc is not None:
                    features.append(mfcc)
                    labels.append(label)

    X = np.array(features)
    y = np.array(labels)

    print("✅ Dataset loaded successfully!")
    print(f"Total samples: {len(X)}")

    # Encode labels
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Save encoder for later use
    joblib.dump(le, "model/label_encoder.pkl")

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    np.save("model/X_train.npy", X_train)
    np.save("model/X_test.npy", X_test)
    np.save("model/y_train.npy", y_train)
    np.save("model/y_test.npy", y_test)

    print("📦 Saved preprocessed data.")
    return X_train, X_test, y_train, y_test
