import random
from datetime import timedelta
import pandas as pd

credit_score = 710
age = 42

def fraud_purchase(current_date, balance):
    location = [
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

    random_location = random.choice(location)

    names = [
        'Paypal',
        'Online',
        'Valley',
        'Unknown',
        'User',
        'ComputerPart',
        'Free Bitcoin'
    ]

    random_name = random.choice(names)

    hour = random.randint(0, 5)
    minute = random.randint(0, 59)
    time = f"{hour:02d}:{minute:02d}:00"
    amount = round(-random.uniform(100, 1800), 2)

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
        "Shopping": ["Amazon", "Target", "Best Buy", "Walmart", "Home Depot", "Petco"],
        "Groceries": ["Kroger", "Publix", "Trader Joe's", "Whole Foods", "Lowes Foods"],
        "Food": ["McDonald's", "Starbucks", "Subway", "Panera", "Smoothie King", "Qdoba"],
        "Gas": ["Shell", "BP", "Chevron", "Exxon", "7-Eleven", "Racetrac", "Wawa"],
        "Car Expense": ["AutoZone", "Midas", "Pep Boys", "Take5", "Valvoline"],
        "Entertainment": ["Movie Theater", "Concert Tickets", "Disney World", "Movie Rental"],
        "Miscellaneous": ["Walgreens", "CVS", "Dollar Tree", "Five Below", "Gamestop"]
    }

    # Pick a random category based on weights
    category = random.choices(list(categories.keys()), weights=list(weights.values()))[0]
    name = random.choice(categories[category])
    
    # Assign a spending range based on the category
    match category:
        case "Shopping":
            amount = round(-random.uniform(10, 150), 2)
        case "Groceries":
            amount = round(-random.uniform(30, 100), 2)
        case "Food":
            amount = round(-random.uniform(5, 40), 2)
        case "Gas":
            amount = round(-random.uniform(10, 30), 2)
        case "Car Expense":
            amount = round(-random.uniform(40, 200), 2)
        case "Entertainment":
            amount = round(-random.uniform(10, 60), 2)
        case _:
            amount = round(-random.uniform(5, 50), 2)

    # Modify spending amounts based on credit score and balance
    credit_mod = 800 / credit_score
    balance_mod = 1

    if balance > 6000:
        balance_mod = 1.5
    elif balance > 8000:
        balance_mod = 2
    elif balance > 10000:
        balance_mod = 2.5
    elif balance > 12000:
        balance_mod = 3

    amount = round(amount * balance_mod * credit_mod, 2)
    balance = round(balance + amount, 2)
    
    # Choose spending hours for a particular user
    hours_start = age % 24
    hours_end = (age + 6) % 24

    if hours_start > hours_end:
        hours_temp = hours_start
        hours_start = hours_end
        hours_end = hours_temp

    hour = random.randint(hours_start, hours_end)
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
    
    # Get car and rent costs based on age, credit, and income
    balance = 3745.87
    paycheck_amount = 3000.00
    car = round((-paycheck_amount / 12) * (800 / credit_score), 2)
    rent = round((-paycheck_amount / 2) * (40 / age), 2)

    recurring_bills = {
        "Car": car,
        "Rent": rent,
        "Spotify": -12,
        "Insurance": -200,
        "Utilities": round(rent / 10, 2),
        "Internet": -70,
        "Streaming": round(-25 * (40 / age), 2),
    }

    # Dates for recurring bills
    day_1_bills = ["Rent", "Insurance", "Car", "Utilities"]
    day_7_bills = ["Spotify", "Internet", "Streaming"]

    current_date = pd.to_datetime("2012-01-01")
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

        # Add a number of random purchases each day
        num_rand = random.randint(0, 5)
        i = 0
        while i < num_rand:
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

        # Insert fraud transactions randomly
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

result = generate_transactions(num_entries=1000)

output_file = 'transactionsPredict.csv'
result.to_csv(output_file, index=False)
