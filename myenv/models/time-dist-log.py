import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import importlib
utils = importlib.import_module('utils.api')
check_company_legitimacy = utils.check_company_legitimacy

def process_data(data):
    # Extract the time features
    data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format='%Y-%m-%d %H:%M:%S')
    data['Hour'] = data['DateTime'].dt.hour
    data['DayOfWeek'] = data['DateTime'].dt.dayofweek

    data['Amount'] = data['Amount'].abs()

    # Calculate usual shopping time (i.e, 10AM - 6PM) and hour tolerance
    usual_hour = data['Hour'].mode()[0]
    hour_tolerance = data['Hour'].std() if data['Hour'].std() > 0 else 1

    # Gather the most usual locations by frequency
    loc_counts = data['Location'].value_counts()
    usual_locs = loc_counts[loc_counts > 1].index.tolist()

    # Getting the mean and std for Amt/hour spent to calc z-score
    amount_stats = data.groupby('Hour')['Amount'].agg(['mean', 'std']).rename(columns={'mean': 'amount_mean', 'std': 'amount_std'})
    data = data.merge(amount_stats, on='Hour', how='left')
    amount_stats['amount_std'] = amount_stats['amount_std'].replace(0, 1e-6)
    print(amount_stats)

    # Check to see if company exists
    data['Company_Exists'] = data['Name'].apply(check_company_legitimacy)
    print(data['Company_Exists'])
    data['Company_Exists'] = (data['Company_Exists'] == 'Yes').astype(int)

    # Now we create these new features from the data we scrapped
    data['Amt_To_Hour_Zscore'] = ((data['Amount'] - data['amount_mean']) / data['amount_std'])
    data['Amt_To_Hour_Zscore'] = data['Amt_To_Hour_Zscore'].clip(-1e6, 1e6)

    data['Usual_Location'] = data['Location'].apply(lambda x: 1 if x in usual_locs else 0)
    data['Unusual_Time'] = (abs(data['Hour'] - usual_hour) > hour_tolerance).astype(int)
    data['Out_of_bounds'] = ((~data['Location'].isin(usual_locs)) & (abs(data['Hour'] - usual_hour) > hour_tolerance)).astype(int)

    high_freq_locations = data['Location'].where(data['Location'].isin(usual_locs))
    location_dummies = pd.get_dummies(high_freq_locations, prefix='Location')
    data = pd.concat([data, location_dummies], axis=1)

    # Get our features for X
    X = pd.concat([data[['Amount', 'Hour', 'DayOfWeek', 'Amt_To_Hour_Zscore', 
                         'Usual_Location', 'Unusual_Time', 'Out_of_bounds', 'Company_Exists']], location_dummies], axis=1)
    y = data['Fraud']

    return X, y, usual_hour, hour_tolerance, usual_locs, amount_stats

def predict_fraud_probability(transaction, usual_hour, hour_tolerance, usual_locations, amount_stats):
    
    # Grab the features out of the test transaction
    transaction['DateTime'] = pd.to_datetime(transaction['DateTime'], format='%Y-%m-%d %H:%M:%S')
    transaction['Hour'] = transaction['DateTime'].hour
    transaction['DayOfWeek'] = transaction['DateTime'].dayofweek
    transaction['Amount'] = abs(transaction['Amount'])

    # Determine out engineered features
    usual_loc = 1 if transaction['Location'] in usual_locations else 0
    unusual_time = 1 if abs(transaction['Hour'] - usual_hour) > hour_tolerance else 0

    if transaction['Hour'] in amount_stats.index:
        mean_amt = amount_stats.loc[transaction['Hour'], 'amount_mean']
        std_amt = amount_stats.loc[transaction['Hour'], 'amount_std']
    else:
        mean_amt = amount_stats['amount_mean'].mean()
        std_amt = amount_stats['amount_std'].mean()

    Amt_To_Hour_Zscore = (transaction['Amount'] - mean_amt) / std_amt
    Amt_To_Hour_Zscore = np.clip(Amt_To_Hour_Zscore, -1e6, 1e6)

    out_of_bounds = 1 if (unusual_time and not usual_loc) else 0

    # Check company exists
    company_exists = check_company_legitimacy(transaction['Name'])
    company_exists = 1 if company_exists == 'Yes' else 0

    features = pd.DataFrame({
        'Amount': [transaction['Amount']],
        'Hour': [transaction['Hour']],
        'DayOfWeek': [transaction['DayOfWeek']],
        'Amt_To_Hour_Zscore': [Amt_To_Hour_Zscore],
        'Usual_Location': [usual_loc],
        'Unusual_Time': [unusual_time],
        'Out_of_bounds': [out_of_bounds],
        'Company_Exists': [company_exists]
    })

    for loc in usual_locations:
        features[f'Location_{loc}'] = 1 if transaction['Location'] == loc else 0

    for col in X.columns:
        if col not in features.columns:
            features[col] = 0

    features = features.reindex(columns=X.columns, fill_value=0)

    features_scaled = scaler.transform(features)

    # Debug prints
    print("Features for prediction:")
    print(features)
    print("Scaled features for prediction:")
    print(features_scaled)

    # Get the probability of this transaction
    fraud_probability = model.predict_proba(features_scaled)[0, 1]

    if not company_exists:
        fraud_probability = max(fraud_probability, 0.9)
    
    return fraud_probability

# Read in our data, and process it
data = pd.read_csv('transactions.csv')
X, y, usual_hour, hour_tolerance, usual_locations, amount_stats = process_data(data)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale our sets
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Fit the model to the data, n_estimators is the number of trees, making a class prediction independenlty
model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

# Print feature importances
feature_importances = pd.DataFrame({'feature': X.columns, 'importance': model.feature_importances_})
feature_importances = feature_importances.sort_values('importance', ascending=False)
print("\nTop 10 Most Important Features:")
print(feature_importances.head(10))

test_transaction = {
    'DateTime': '2024-7-12 22:30:00',
    'Amount': 12,
    'Location': 'Atlanta GA'
}

test_transaction2 = {
    'DateTime': '2024-7-12 18:30:00',
    'Amount': 200,
    'Location': 'Orlando FL'
}

test_transaction3 = {
    'DateTime': '2024-7-12 04:30:00',
    'Amount': 100000,
    'Location': 'Orlando FL'
}

fraud_prob = predict_fraud_probability(test_transaction, usual_hour, hour_tolerance, usual_locations, amount_stats)
print(f"Probability of fraud for the new transaction: {fraud_prob:.4f}\n")

fraud_prob = predict_fraud_probability(test_transaction2, usual_hour, hour_tolerance, usual_locations, amount_stats)
print(f"Probability of fraud for the new transaction: {fraud_prob:.4f} \n")

fraud_prob = predict_fraud_probability(test_transaction3, usual_hour, hour_tolerance, usual_locations, amount_stats)
print(f"Probability of fraud for the new transaction: {fraud_prob:.4f}\n")