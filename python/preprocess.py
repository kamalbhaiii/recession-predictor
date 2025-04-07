import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle
from dotenv import load_dotenv
import os

load_dotenv()


data = pd.read_csv(os.getenv('PYTHON_PREPROCESSING_DATA'))  
data['date'] = pd.to_datetime(data['date'])
data.set_index('date', inplace=True)


data['recession'] = 0
for i in range(6, len(data)):
    if data['cpi'].iloc[i-6:i].pct_change().mean() < 0: 
        data['recession'].iloc[i] = 1


features = data[['cpi', 'bond', 'm3', 'interest', 'wti']].values
labels = data['recession'].values


scaler = MinMaxScaler()
features_scaled = scaler.fit_transform(features)


def create_sequences(data, labels, seq_length=12):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(labels[i + seq_length])
    return np.array(X), np.array(y)

seq_length = 12
X, y = create_sequences(features_scaled, labels, seq_length)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Save preprocessed data (optional, for debugging)
# np.save('X_train.npy', X_train)
# np.save('X_test.npy', X_test)
# np.save('y_train.npy', y_train)
# np.save('y_test.npy', y_test)

with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Train the LSTM model
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

model = Sequential()
model.add(LSTM(100, return_sequences=True, input_shape=(seq_length, X.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(100))
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test), verbose=1)
model.save('recession_lstm_model.h5')

print("Preprocessing and training complete. Model saved as 'recession_lstm_model.h5'.")