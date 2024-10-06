import random
from datetime import timedelta
import pandas as pd

credit_score = 610

def fraud_purchase(current_date, balance):
    location_zip = [
        'Pyongyang NK',
        'Los Angeles CA',
        'New York NY',
        'London EN',
        'Pittsburgh PA',
        'Honolulu HI',
        'Tokyo JP',
        'Charleston SC',
        'Mexico City MC',
        'Anchorage AL',
        'Groton CT'
    ]

    random_location = random.choice(location_zip)

    names = [
        'Paypal',
        'Accelerators',
        'Monster Energy',
        'Fat Joe',
        'Skinny Joe',
        'Fraud',
        'Servicenow',
        'IBM',
        'Magic the Gathering',
        'Pawn Stars',
        'Lockheed Martin',
        'Impractical Jokers'
    ]

    random_name = random.choice(names)

    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    time = f"{hour:02d}:{minute:02d}:00"
    amount = round(-random.uniform(100, 3000), 2)

    return {
        "Date": current_date.date(),
        "Time": time,
        "Name": random_name,
        "Amount": amount,
        "Location": random_location,
        "Zip": random.randint(11111, 99999),
        "Balance": round(balance + amount, 2)
    }, balance

def random_purchase(current_date, balance, weights):
    location_zip = {
        'Oviedo FL': '32765',
        'Orlando FL': '32816',
        'Winter Park FL': '32789'
    }

    random_location = random.choice(list(location_zip.keys()))
    zip_code = location_zip[random_location]

    categories = {
        "Shopping": ["Amazon", "Target", "Best Buy", "Walmart", "Michael's", "Home Depot", "Petco"],
        "Groceries": ["Kroger", "Publix", "Trader Joe's", "Whole Foods", "Lowes Foods"],
        "Food": ["McDonald's", "Starbucks", "Burger King", "Subway", "Scooter's", "Panera", "Smoothie King", "Panda Express", "Qdoba"],
        "Gas": ["Shell", "BP", "Chevron", "Exxon", "7-Eleven", "Racetrac", "Wawa"],
        "Car Expense": ["AutoZone", "Jiffy Lube", "Midas", "Pep Boys", "Take5", "Valvoline"],
        "Entertainment": ["Movie Theater", "Concert Tickets", "Disney World", "Netflix", "Movie Rental"],
        "Miscellaneous": ["Walgreens", "CVS", "Dollar Tree", "Five Below", "Gamestop", "WOTC"]
    }

    # Pick a random category based on weights
    category = random.choices(list(categories.keys()), weights=list(weights.values()))[0]
    name = random.choice(categories[category])
    
    # Assign a spending range based on the category
    # Randomness could be modified depending on credit score, age, and location
    if category == "Shopping":
        amount = round(-random.uniform(10, 150), 2)
    elif category == "Groceries":
        amount = round(-random.uniform(30, 100), 2)
    elif category == "Food":
        amount = round(-random.uniform(5, 40), 2)
    elif category == "Gas":
        amount = round(-random.uniform(10, 30), 2)
    elif category == "Car Expense":
        amount = round(-random.uniform(40, 200), 2)
    elif category == "Entertainment":
        amount = round(-random.uniform(10, 60), 2)
    else:  # Miscellaneous
        amount = round(-random.uniform(5, 50), 2)
    if balance > 6000:
        amount = round(amount * 1.5 * (800 / credit_score), 2)
    elif balance > 8000:
        amount = round(amount * 2.5 * (800 / credit_score), 2)
    elif balance > 10000:
        amount = round(amount * 3.5 * (800 / credit_score), 2)
    elif balance > 12000:
        amount = round(amount * 5.5 * (800 / credit_score), 2)
    balance = round(balance + amount, 2)
    
    # Generate a random time between 9am and 11pm
    if credit_score < 650:
        hour = random.randint(round(9 - 800 / credit_score), round(20 + 800 / credit_score))
    else:
        hour = random.randint(round(10 + credit_score / 800), round(18 - credit_score / 800))
    minute = random.randint(0, 59)
    time = f"{hour:02d}:{minute:02d}:00"

    return {
        "Date": current_date.date(),
        "Time": time,
        "Name": name,
        "Amount": amount,
        "Location": random_location,
        "Zip": zip_code,
        "Balance": balance
    }, balance

def generate_transactions(num_entries=100, weights=None):
    # weights can be modified based on credit score, age, income, and location
    if weights is None:
        weights = {
            "Shopping": 1.5,
            "Groceries": 1,
            "Food": 3,
            "Gas": 1,
            "Car Expense": 0.5,
            "Entertainment": 1,
            "Miscellaneous": 1
        }

    data = {
        "Date": [],
        "Time": [],
        "Name": [],
        "Amount": [],
        "Location": [],
        "Zip": [],
        "Balance": [],
        "Fraud": []
    }
    
    balance = 2000.00
    paycheck_amount = 2000.00
    recurring_bills = {
        "Car": -300.00,
        "Rent": -960.00,
        "Spotify": -11.99,
        "Insurance": -197.46,
        "Internet": -70.89,
        "ChatGPT Plus": -20.00
    }

    # Dates for recurring bills
    day_1_bills = ["Rent", "Insurance", "Car"]
    day_7_bills = ["Spotify", "Internet", "ChatGPT Plus"]

    current_date = pd.to_datetime("2024-01-01")
    paycheck_date = current_date

    while len(data["Date"]) < num_entries:
        # Add paycheck every 2 weeks
        if current_date == paycheck_date:
            balance = round(balance + paycheck_amount, 2)
            data["Date"].append(paycheck_date.date())
            data["Time"].append("08:00:00")
            data["Name"].append("Paycheck")
            data["Amount"].append(paycheck_amount)
            data["Location"].append("Oviedo FL")
            data["Zip"].append(32765)
            data["Balance"].append(balance)
            data["Fraud"].append(0)
            paycheck_date += timedelta(days=14)

        # Add recurring bills on the 1st of the month
        if current_date.day == 1:
            for bill in day_1_bills:
                amount = recurring_bills[bill]
                balance = round(balance + amount, 2)
                data["Date"].append(current_date.date())
                data["Time"].append("09:00:00")
                data["Name"].append(bill)
                data["Amount"].append(amount)
                data["Location"].append("Oviedo FL")
                data["Zip"].append(32765)
                data["Balance"].append(balance)
                data["Fraud"].append(0)

        # Add recurring bills on the 7th of the month
        if current_date.day == 7:
            for bill in day_7_bills:
                amount = recurring_bills[bill]
                balance = round(balance + amount, 2)
                data["Date"].append(current_date.date())
                data["Time"].append("09:00:00")
                data["Name"].append(bill)
                data["Amount"].append(amount)
                data["Location"].append("Oviedo FL")
                data["Zip"].append(32765)
                data["Balance"].append(balance)
                data["Fraud"].append(0)

        # Add a random purchase 0-3 times per day
        num_rand = random.randint(0, 3)

        i = 0
        while i < num_rand:
            if random.randint(1, 10) == 1:
                fraud_transaction, balance = fraud_purchase(current_date, balance)
                data["Date"].append(fraud_transaction["Date"])
                data["Time"].append(fraud_transaction["Time"])
                data["Name"].append(fraud_transaction["Name"])
                data["Amount"].append(fraud_transaction["Amount"])
                data["Location"].append(fraud_transaction["Location"])
                data["Zip"].append(fraud_transaction["Zip"])
                data["Balance"].append(fraud_transaction["Balance"])
                data["Fraud"].append(1)

            random_transaction, balance = random_purchase(current_date, balance, weights)
            data["Date"].append(random_transaction["Date"])
            data["Time"].append(random_transaction["Time"])
            data["Name"].append(random_transaction["Name"])
            data["Amount"].append(random_transaction["Amount"])
            data["Location"].append(random_transaction["Location"])
            data["Zip"].append(random_transaction["Zip"])
            data["Balance"].append(random_transaction["Balance"])
            data["Fraud"].append(0)
            i = i + 1
        if random.randint(1, 10) == 1:
            fraud_transaction, balance = fraud_purchase(current_date, balance)
            data["Date"].append(fraud_transaction["Date"])
            data["Time"].append(fraud_transaction["Time"])
            data["Name"].append(fraud_transaction["Name"])
            data["Amount"].append(fraud_transaction["Amount"])
            data["Location"].append(fraud_transaction["Location"])
            data["Zip"].append(fraud_transaction["Zip"])
            data["Balance"].append(fraud_transaction["Balance"])
            data["Fraud"].append(1)
        current_date += timedelta(days=1)

    return pd.DataFrame(data)

result = generate_transactions(num_entries=10000)

output_file = 'transactions.csv'
result.to_csv(output_file, index=False)
