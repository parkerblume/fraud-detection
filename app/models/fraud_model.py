import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from imblearn.over_sampling import SMOTE
import sys
import os
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from app.utils.api import check_company_legitimacy


def process_data(data, user_details):
    '''
    Preprocesses the data to extract features, and engineer a few extra features
    to get the most useful inputs in determining fraud
    '''

    # Extract the time features
    data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format='%Y-%m-%d %H:%M:%S')
    data['Hour'] = data['DateTime'].dt.hour
    data['DayOfWeek'] = data['DateTime'].dt.dayofweek

    data['Amount'] = data['Amount'].abs()

    data['credit_score'] = user_details['credit_score']
    data['age'] = user_details['age']

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
                         'Usual_Location', 'Unusual_Time', 'Out_of_bounds', 'credit_score', 'age']], location_dummies], axis=1)
    y = data['Fraud']

    return X, y, usual_hour, hour_tolerance, usual_locs, amount_stats

def predict_fraud_probability(transaction, X, model, scaler, user_details, usual_hour, hour_tolerance, usual_locations, amount_stats):
    
    # Grab the features out of the test transaction
    transaction['DateTime'] = pd.to_datetime(transaction['DateTime'], format='%Y-%m-%d %H:%M:%S')
    transaction['Hour'] = transaction['DateTime'].hour
    transaction['DayOfWeek'] = transaction['DateTime'].dayofweek
    transaction['Amount'] = abs(transaction['Amount'])
    transaction['credit_score'] = user_details['credit_score']
    transaction['age'] = user_details['age']

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
        'Company_Exists': [company_exists],
        'credit_score': [user_details['credit_score']],
        'age': [user_details['age']]
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

    # basically can assume this is a fraud charge
    if not company_exists:
        fraud_probability = max(fraud_probability, 0.9)
    
    fraud_probability = adjust_prob_by_risks(fraud_probability, calc_cred_risk(transaction['credit_score']), calculate_age_risk(transaction['age']))

    return fraud_probability

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Scale our sets
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)

    # Print class distribution before and after SMOTE
    print("Class distribution before SMOTE:")
    print(pd.Series(y_train).value_counts(normalize=True))
    print("\nClass distribution after SMOTE:")
    print(pd.Series(y_train_resampled).value_counts(normalize=True))

    # Fit the model to the data, n_estimators is the number of trees, making a class prediction independenlty
    model = RandomForestClassifier(n_estimators=100, min_samples_leaf=5, max_depth=3, class_weight="balanced_subsample", random_state=42)
    model.fit(X_train_resampled, y_train_resampled)

    return model, scaler, X_test_scaled, y_test

def test_model(model, X_test_scaled, y_test, feature_names):
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

    # Generate classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    roc_auc = roc_auc_score(y_test, y_pred_proba)
    print(f"ROC AUC Score: {roc_auc:.4f}")

    feature_importances = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    })
    feature_importances = feature_importances.sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importances.head(10))

    return y_pred, y_pred_proba, roc_auc, feature_importances

def calc_cred_risk(credit_score):
    if credit_score < 580:
        return 0.2
    elif 580 <= credit_score < 670:
        return 0.1
    elif 670 <= credit_score < 740:
        return 0
    elif 740 <= credit_score < 800:
        return -0.1
    else:
        return -0.15
    
def calculate_age_risk(age):
    if age < 18:
        return 0.3
    elif 18 <= age < 25:
        return 0.2
    elif 25 <= age < 60:
        return 0
    else:
        return 0.3
    
def adjust_prob_by_risks(probability, credit_risk, age_risk):
    credit_risk = calc_cred_risk(credit_risk)
    age_risk = calculate_age_risk(age_risk)
    
    # Combine risks, giving slightly more weight to credit score
    combined_risk = (credit_risk * 0.6) + (age_risk * 0.4)
    
    # Adjust probability
    adjusted_probability = probability + (combined_risk * 0.1)
    
    # Ensure probability stays within [0, 1]
    return max(0, min(1, adjusted_probability))

# Read in our data, and process it
# data = pd.read_csv('transactions_credit.csv')
# X, y, usual_hour, hour_tolerance, usual_locations, amount_stats = process_data(data, user_details)
# model, scaler, X_test_scaled, y_test = train_model(X, y)

# Test Model
# y_pred, y_pred_proba, roc_auc, feature_importances = test_model(model, X_test_scaled, y_test, X.columns)


# y_pred = model.predict(X_test_scaled)
# y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

# print("\nClassification Report:")
# print(classification_report(y_test, y_pred))
# print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
# 
# # Print feature importances
# feature_importances = pd.DataFrame({'feature': X.columns, 'importance': model.feature_importances_})
# feature_importances = feature_importances.sort_values('importance', ascending=False)
# print("\nTop 10 Most Important Features:")
# print(feature_importances.head(20))

# test_transaction = {
#     'DateTime': '2024-7-12 22:30:00',
#     'Name': 'Wawa',
#     'Amount': 12,
#     'Location': 'Atlanta GA'
# }
# 
# test_transaction2 = {
#     'DateTime': '2024-7-12 18:30:00',
#     'Name': 'ChairMan',
#     'Amount': 200,
#     'Location': 'Orlando FL'
# }
# 
# test_transaction3 = {
#     'DateTime': '2024-7-12 04:30:00',
#     'Name': 'Lexus',
#     'Amount': 1000000,
#     'Location': 'Orlando FL'
# }
# 
# test_transaction4 = {
#     'DateTime': '2024-7-12 16:30:00',
#     'Name': 'Wawa',
#     'Amount': 40,
#     'Location': 'Orlando FL'
# }
# 
# fraud_prob = predict_fraud_probability(test_transaction, user_details, usual_hour, hour_tolerance, usual_locations, amount_stats)
# print(f"Probability of fraud for the new transaction: {fraud_prob:.4f}\n")
# 
# fraud_prob = predict_fraud_probability(test_transaction2, user_details, usual_hour, hour_tolerance, usual_locations, amount_stats)
# print(f"Probability of fraud for the new transaction: {fraud_prob:.4f} \n")
# 
# fraud_prob = predict_fraud_probability(test_transaction3, user_details, usual_hour, hour_tolerance, usual_locations, amount_stats)
# print(f"Probability of fraud for the new transaction: {fraud_prob:.4f}\n")
# 
# fraud_prob = predict_fraud_probability(test_transaction4, user_details, usual_hour, hour_tolerance, usual_locations, amount_stats)
# print(f"Probability of fraud for the new transaction: {fraud_prob:.4f}\n")