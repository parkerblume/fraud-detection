import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Load the dataset
data = pd.read_csv('transactions.csv')

# Preprocessing - Feature Engineering
# Convert Date and Time into useful features
data['Date'] = pd.to_datetime(data['Date'])
data['Transaction_Year'] = data['Date'].dt.year
data['Transaction_Month'] = data['Date'].dt.month
data['Transaction_Day'] = data['Date'].dt.day
data['Transaction_Hour'] = pd.to_datetime(data['Time']).dt.hour

# Location-based features (This assumes 'Location' is a string, so you may need to adjust it)
# For simplicity, let's say "User_Location" and "Transaction_Location" are numerical or categorical. 
# You can calculate distance if you have lat/long values.
data['Location_Match'] = np.where(data['Location'] == data['User_Location'], 1, 0)

# Selecting relevant features for fraud detection
features = [
    'Amount', 
    'Balance', 
    'Transaction_Hour', 
    'Transaction_Month', 
    'Transaction_Day', 
    'Income', 
    'Credit_Score', 
    'Age', 
    'Location_Match'
]

X = data[features]
y = data['Fraudulent']  # Assuming your CSV has a column named 'Fraudulent' that is the target label

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training with Random Forest
rf_model = RandomForestClassifier(random_state=42, class_weight='balanced')  # 'balanced' helps with fraud detection
rf_model.fit(X_train, y_train)

# Predictions
y_pred = rf_model.predict(X_test)

# Evaluation
print("Model Performance on Test Set")
print(classification_report(y_test, y_pred))

# Detecting fraud on the whole dataset (i.e., finding suspected fraudulent transactions)
data['Predicted_Fraud'] = rf_model.predict(X)

# Print out the suspected fraudulent transactions
fraud_transactions = data[data['Predicted_Fraud'] == 1]

print("Suspected Fraudulent Transactions:")
print(fraud_transactions)
