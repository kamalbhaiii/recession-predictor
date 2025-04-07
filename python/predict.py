import sys
import json
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from dotenv import load_dotenv
import os

load_dotenv()

print("Python script started...")

try:
    # Load scaler
    print("Loading scaler...")
    with open(os.getenv('PYTHON_PKL_FILE'), 'rb') as f:
        scaler = pickle.load(f)

    print("Scaler loaded successfully.")

    # Load model
    print("Loading model...")
    model = tf.keras.models.load_model(os.getenv('PYTHON_LSTM_MODEL'))

    print("Model loaded successfully.")

    # Get input
    print("Parsing input features...")
    features = json.loads(sys.argv[1])
    print("Received features:", features)

    features_array = np.array([[f['gdp'], f['inflation'], f['unemployment']] for f in features])
    print("Converted to numpy array:", features_array)

    # Normalize input
    print("Scaling features...")
    features_scaled = scaler.transform(features_array)
    print("Scaled features:", features_scaled)

    # Reshape for LSTM
    input_data = features_scaled.reshape((1, 12, 3))
    print("Reshaped input for LSTM:", input_data.shape)

    # Predict
    print("Making prediction...")
    prediction = model.predict(input_data, verbose=0)[0][0]
    print("Prediction result:", prediction)

except Exception as e:
    print("Error in Python script:", str(e))
    sys.exit(1)
