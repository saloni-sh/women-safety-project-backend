# train_model.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from preprocess import load_data

def build_model(input_shape, num_classes):
    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2,2)),
        Dropout(0.3),

        Conv2D(64, (3,3), activation='relu'),
        MaxPooling2D((2,2)),
        Dropout(0.3),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_data("dataset")

    X_train = X_train[..., np.newaxis]
    X_test = X_test[..., np.newaxis]

    model = build_model((40, 50, 1), num_classes=len(set(y_train)))
    model.summary()

    print("🚀 Training started...")
    history = model.fit(X_train, y_train, epochs=30, batch_size=16, validation_data=(X_test, y_test))

    # Evaluate
    loss, acc = model.evaluate(X_test, y_test)
    print(f"✅ Test Accuracy: {acc * 100:.2f}%")

    # Save model
    model.save("model/voice_model.h5")
    print("💾 Model saved to model/voice_model.h5")
