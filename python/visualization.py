import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Ensure export directory exists
EXPORT_DIR = 'exports'
os.makedirs(EXPORT_DIR, exist_ok=True)

# Load dataset
data = pd.read_csv(os.getenv('PYTHON_PREPROCESSING_DATA'))

# Preprocessing
data['date'] = pd.to_datetime(data['date'])
data.set_index('date', inplace=True)

# # Recession indicator logic
# data['recession'] = 0
# for i in range(6, len(data)):
#     if data['cpi'].iloc[i-6:i].pct_change().mean() < 0: 
#         data.iloc[i, data.columns.get_loc('recession')] = 1

# Plotting function
def plot_time_series(df, column, title, ylabel, filename):
    df[column] = df[column]*100
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=df.index, y=column, data=df)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(os.path.join(EXPORT_DIR, filename), format='jpg')
    plt.close()

# Generate graphs
plot_time_series(data, 'm3', 'M3 Money Supply Over Time', 'M3 Change (%)', 'm3_money_supply.jpg')
plot_time_series(data, 'bond', 'Bond Yield Over Time', 'Bond Yield Change (%)', 'bond_yield_trend.jpg')
plot_time_series(data, 'interest', 'Interest Rate Over Time', 'Interest Rate Change (%)', 'interest_rate_fluctuation.jpg')
plot_time_series(data, 'cpi', 'Consumer Price Index (CPI) Over Time', 'CPI Change (%)', 'cpi_trend.jpg')
