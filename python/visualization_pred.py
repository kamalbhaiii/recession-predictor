import os
import json
import sys
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tensorflow as tf
from dotenv import load_dotenv
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.seasonal import seasonal_decompose

# Load environment variables
load_dotenv()

# Create exports directory if not exists
os.makedirs("exports", exist_ok=True)

# Load data
data = pd.read_csv(os.getenv('PYTHON_PREPROCESSING_DATA'))
data['date'] = pd.to_datetime(data['date'])
data.set_index('date', inplace=True)

# Drop rows with NaNs
data = data.dropna()

# Optional: Rename columns if needed
# print(data.columns.tolist())

# Load scaler and model
with open(os.getenv('PYTHON_PKL_FILE'), 'rb') as f:
    scaler = pickle.load(f)

model = tf.keras.models.load_model(os.getenv('PYTHON_LSTM_MODEL'))

# Prepare features and labels
features = ['cpi', 'interest', 'wti', 'bond', 'm3']
X_all = data[features]
X_scaled = scaler.transform(X_all)

# Reshape for LSTM: samples = total - window
window_size = 12
X_seq = []
dates_seq = []
for i in range(len(X_scaled) - window_size):
    X_seq.append(X_scaled[i:i+window_size])
    dates_seq.append(data.index[i+window_size])

X_seq = np.array(X_seq)

# Generate predictions
predictions = model.predict(X_seq, verbose=0).flatten()
prediction_labels = (predictions > 0.5).astype(int)

# Add predictions to dataframe
data = data.iloc[window_size:].copy()
data['recession_pred'] = prediction_labels
data['recession_prob'] = predictions

# ----------------- Visualizations -------------------

sns.set(style="darkgrid")

# 1. Correlation Heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(data[features + ['recession_pred']].corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap of Economic Indicators")
plt.tight_layout()
plt.savefig("exports/correlation_heatmap.jpg")
plt.close()

# 2. CPI Trend (2000–2024)
plt.figure(figsize=(10, 5))
sns.lineplot(data=data, x=data.index, y='cpi')
plt.title("Consumer Price Index Trend (2000–2024)")
plt.xlabel("Date")
plt.ylabel("CPI")
plt.tight_layout()
plt.savefig("exports/cpi_trend.jpg")
plt.close()

# 3. M3 vs Interest Rate
plt.figure(figsize=(10, 5))
sns.lineplot(data=data, x=data.index, y='m3', label='M3 Money Supply')
sns.lineplot(data=data, x=data.index, y='interest', label='Interest Rate')
plt.title("M3 Money Supply vs Interest Rates")
plt.xlabel("Date")
plt.ylabel("Value")
plt.legend()
plt.tight_layout()
plt.savefig("exports/m3_vs_interest.jpg")
plt.close()

# 4. Seasonal Decomposition of CPI
decomp = seasonal_decompose(data['cpi'], model='additive', period=12)
decomp.plot()
plt.suptitle("Seasonal Decomposition of CPI", fontsize=16)
plt.tight_layout()
plt.savefig("exports/cpi_seasonal_decomposition.jpg")
plt.close()

# 5. Recession Prediction Output
plt.figure(figsize=(10, 5))
sns.lineplot(data=data, x=data.index, y='recession_prob', label='Recession Probability')
sns.scatterplot(data=data, x=data.index, y='recession_pred', label='Recession Prediction', color='red')
plt.title("Recession Prediction Over Time")
plt.xlabel("Date")
plt.ylabel("Probability / Label")
plt.legend()
plt.tight_layout()
plt.savefig("exports/recession_dashboard_output.jpg")
plt.close()

# 6. ROC Curve
y_true = data['recession'].values[window_size:]  # Adjusted true values
min_len = min(len(y_true), len(predictions))
y_true = y_true[:min_len]
predictions = predictions[:min_len]

fpr, tpr, thresholds = roc_curve(y_true, predictions)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(6, 6))
plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve for LSTM Recession Model")
plt.legend()
plt.tight_layout()
plt.savefig("exports/roc_curve.jpg")
plt.close()

# 7. Confusion Matrix
min_len = min(len(y_true), len(predictions))

y_true = y_true[:min_len]
predictions = predictions[:min_len]
prediction_labels = (predictions > 0.5).astype(int)

cm = confusion_matrix(y_true, prediction_labels)
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap="Blues")
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig("exports/confusion_matrix.jpg")
plt.close()

print("✅ All charts saved to 'exports' folder successfully.")
