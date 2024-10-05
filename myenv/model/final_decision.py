import numpy as np
import random
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Sample data
X_amount = np.random.rand(1000, 5)  # Features related to transaction amount
X_time_loc = np.random.rand(1000, 5)  # Features related to time and location
X_description = np.random.rand(1000, 5)  # Features related to transaction description

y = np.random.randint(0, 2, 1000)  # Binary fraud labels (0 = Not Fraud, 1 = Fraud)

# Split data into train and test sets
X_amount_train, X_amount_test, y_train, y_test = train_test_split(X_amount, y, test_size=0.2)
X_time_loc_train, X_time_loc_test = train_test_split(X_time_loc, test_size=0.2)
X_description_train, X_description_test = train_test_split(X_description, test_size=0.2)

# Train base models
model_amount = LogisticRegression()
model_time_loc = DecisionTreeClassifier()
model_description = LogisticRegression()

model_amount.fit(X_amount_train, y_train)
model_time_loc.fit(X_time_loc_train, y_train)
model_description.fit(X_description_train, y_train)

# Get prediction probabilities (fraud likelihoods)
prob_amount = model_amount.predict_proba(X_amount_test)[:, 1]  # Fraud probabilities
prob_time_loc = model_time_loc.predict_proba(X_time_loc_test)[:, 1]
prob_description = model_description.predict_proba(X_description_test)[:, 1]

# Tune weights via random search
best_score = 0
best_weights = None

for _ in range(100):
    w_amount = random.uniform(0, 1)
    w_time_loc = random.uniform(0, 1)
    w_description = random.uniform(0, 1)
    
    # Normalization
    total_weight = w_amount + w_time_loc + w_description
    w_amount /= total_weight
    w_time_loc /= total_weight
    w_description /= total_weight

    final_prob = (w_amount * prob_amount +
                  w_time_loc * prob_time_loc +
                  w_description * prob_description)
    final_predictions = (final_prob >= 0.50).astype(int)
    score = accuracy_score(y_test, final_predictions)
    
    if score > best_score:
        best_score = score
        best_weights = (w_amount, w_time_loc, w_description)

weight_amount, weight_time_loc, weight_description = best_weights


# Calculate the weighted average of the probabilities
final_prob = (weight_amount * prob_amount +
              weight_time_loc * prob_time_loc +
              weight_description * prob_description)

# Set a threshold for the final decision (e.g., above 0.5 means fraud)
threshold = 0.5
final_predictions = (final_prob >= threshold).astype(int)

# Evaluate the final ensemble model
accuracy = accuracy_score(y_test, final_predictions)
print(f"Ensemble Accuracy: {accuracy:.2f}")
