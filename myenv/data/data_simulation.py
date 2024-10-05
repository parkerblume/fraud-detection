import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_transaction_data(num_transactions=1000, fraud_probability=0.05):
    transactions = []
    
    # Define common merchants, locations, and possible transaction ranges
    merchants = ['Amazon', 'Walmart', 'Target', 'Apple Store', 'Best Buy', 'Starbucks', 'Uber']
    locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Seattle', 'San Francisco']
    categories = ['electronics', 'groceries', 'transportation', 'restaurants', 'clothing']
    
    for _ in range(num_transactions):
        # Randomly generate transaction details
        transaction_date = fake.date_time_between(start_date='-30d', end_date='now')
        transaction_amount = round(random.uniform(5.0, 500.0), 2)
        merchant = random.choice(merchants)
        location = random.choice(locations)
        description = fake.sentence(nb_words=5)
        transaction_time = transaction_date.time()
        category = random.choice(categories)
        
        # Randomly determine if transaction is fraudulent based on fraud_probability
        is_fraud = 1 if random.uniform(0, 1) < fraud_probability else 0
        
        # Create some "fraud indicators" if is_fraud == 1
        if is_fraud:
            # Fraudulent transactions might have unusual amounts, locations, etc.
            transaction_amount = round(random.uniform(1000.0, 5000.0), 2)  # Large amounts
            location = random.choice(['Moscow', 'Lagos', 'Shanghai'])  # Unusual locations
            description = "Suspicious high-value purchase"

        transactions.append({
            'transaction_date': transaction_date.strftime('%Y-%m-%d'),
            'transaction_time': transaction_time.strftime('%H:%M:%S'),
            'merchant': merchant,
            'location': location,
            'amount': transaction_amount,
            'description': description,
            'is_fraud': is_fraud
        })
    
    return pd.DataFrame(transactions)

# Generate 1000 transactions with 5% fraud rate
transactions_df = generate_transaction_data(num_transactions=1000, fraud_probability=0.05)

# Save to CSV
transactions_df.to_csv('transactions.csv', index=False)
print("CSV file generated successfully.")
