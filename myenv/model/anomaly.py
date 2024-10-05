import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

file_path = '../amounts_with_outliers.csv' # 1000 values 1-300 with 7 outliers
data = pd.read_csv(file_path)
amounts = data["Amount"].values.reshape(-1, 1)

iso_forest = IsolationForest(contamination=0.007) # 0.007 = 7 / 1000

# Train model on existing data
iso_forest.fit(amounts)

# Predict on the same dataset
predictions = iso_forest.predict(amounts)

# Identify outliers in the original data
outliers = data[predictions == -1]

print("Outliers in training data:")
print(outliers)

# Test new data
file_path = '../amounts_5000.csv'
new_data = pd.read_csv(file_path)
new_amounts = new_data["Amount"].values.reshape(-1, 1)

new_predictions = iso_forest.predict(new_amounts)
outliers = new_data[new_predictions == -1]

print("Outliers in new data:")
print(outliers)
