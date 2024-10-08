import sys
import os
from pathlib import Path
import requests
import json
import random
import web3

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
from app.models.fraud_model import process_data, train_model, predict_fraud_probability

from web3 import Web3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transaction(BaseModel):
    DateTime: str
    Name: str
    Amount: float
    Location: str
    Zip: int
    Balance: float

# Global variables related to model
user_details = None
model = None
scaler = None
X = None
usual_hour = None
hour_tolerance = None
usual_locations = None
amount_stats = None
transaction_counter = 1

# Company-Address Mapping
company_address_map_file = 'company_address_map.json'
company_address_map = {}

# Load Ethereum addresses from ethereum_addresses.txt
ethereum_addresses_file = '../ethereum_addresses.txt'
ethereum_addresses = []

# Pointer to the next available Ethereum address
address_pointer = 0

def load_ethereum_addresses():
    global ethereum_addresses
    if not os.path.exists(ethereum_addresses_file):
        print(f"Error: {ethereum_addresses_file} not found.")
        sys.exit(1)
    with open(ethereum_addresses_file, 'r') as f:
        ethereum_addresses = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(ethereum_addresses)} Ethereum addresses.")

def load_company_address_map():
    global company_address_map
    if os.path.exists(company_address_map_file):
        with open(company_address_map_file, 'r') as f:
            company_address_map = json.load(f)
        print(f"Loaded company-address mappings for {len(company_address_map)} companies.")
    else:
        company_address_map = {}
        print("No existing company-address map found. Starting fresh.")

def save_company_address_map():
    with open(company_address_map_file, 'w') as f:
        json.dump(company_address_map, f, indent=4)
    print("Company-address mappings saved.")

def get_sender_address(company_name):
    global address_pointer
    # Check if the company already has an assigned address
    if company_name in company_address_map:
        return company_address_map[company_name]
    else:
        # Assign the next available address
        if address_pointer >= len(ethereum_addresses):
            raise Exception("No more Ethereum addresses available to assign.")
        assigned_address = ethereum_addresses[address_pointer]
        address_pointer += 1
        company_address_map[company_name] = assigned_address
        save_company_address_map()
        return assigned_address

# Initialize on startup
load_ethereum_addresses()
load_company_address_map()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/train")
async def train_model_endpoint(file: UploadFile = File(None)):
    global model, X, user_details, scaler, usual_hour, hour_tolerance, usual_locations, amount_stats

    if file:
        file_location = f"data/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
    else:
        file_location = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'transactions.csv')
        if not os.path.exists(file_location):
            raise HTTPException(status_code=404, detail="File is not found")

    data = pd.read_csv(file_location)
    user_details = {
        'Name': 'Alexander Hamilton',
        'credit_score': 650,
        'age': 35
    }
    X, y, usual_hour, hour_tolerance, usual_locations, amount_stats = process_data(data, user_details)
    model, scaler, _, _ = train_model(X, y)

    return {"message": "Your own personal model has been trained to your habits!"}

@app.post("/predict")
async def predict(transaction: Transaction):
    global model, scaler, usual_hour, hour_tolerance, usual_locations, amount_stats, transaction_counter

    print(transaction)

    if model is None:
        raise HTTPException(status_code=400, detail="Model not trained. Please train the model first.")

    transaction_dict = transaction.model_dump()

    probability = predict_fraud_probability(transaction_dict, X, model, scaler, user_details, usual_hour, hour_tolerance, usual_locations, amount_stats)

    is_fraud = 1 if probability > 0.57 else 0

    # Assign sender address based on company name
    try:
        sender = get_sender_address(transaction.Name)
    except Exception as e:
        print(f"Error assigning sender address: {e}")
        raise HTTPException(status_code=500, detail="No available Ethereum addresses to assign.")

    transaction_data = {
        "transactionId": transaction_counter,
        "companyId": transaction.Name,
        "sender": sender,
        "receiver": "0x0B8d325352A71368760C645F3B794FcD44A67934",
        "isFraudulent": is_fraud,
        "amount": transaction.Amount,
        "timestamp": transaction.DateTime
    }
    json_data = json.dumps(transaction_data)

    try:
        response = requests.post(
            "http://localhost:3001/record-transaction",
            data=json_data,
            headers = {
                "Content-Type": "application/json"
            }
        )
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to backend: {e}")
        raise HTTPException(status_code=500, detail="Backend service is unavailable.")

    if response.status_code == 200:
        print("It's public on the blockchain!")
        print("Response:", response.json())
    else:
        print(f"Failed to record transaction: {response.status_code} - {response.text}")
        raise HTTPException(status_code=response.status_code, detail="Failed to record transaction on blockchain.")

    transaction_counter += 1

    return {"fraud_probability": probability}

@app.get("/companies/{companyId}")
async def get_company(companyId: str):
    try:
        company = await companiesCollection.find_one({'companyId': companyId})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"success": True, "company": company}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/get-transaction/{transactionId}")
async def get_transaction(transactionId: int):
    try:
        # Get transaction from smart contract
        transaction = contract.functions.transactions(transactionId).call()

        # Decode companyId from bytes32 to string if necessary
        companyId = Web3.toText(transaction[3]).strip('\x00')  # Adjust the index based on struct

        # Format the data
        transactionData = {
            "id": transaction[0],
            "dataHash": transaction[1],
            "isFraudulent": transaction[2],
            "companyId": companyId
        }

        return {"success": True, "transaction": transactionData}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/get-all-transactions")
async def get_all_transactions():
    try:
        transactionCount = contract.functions.transactionCount().call()
        count = transactionCount

        transactions = []

        for i in range(1, count + 1):
            transaction = contract.functions.transactions(i).call()

            # Decode companyId from bytes32 to string if necessary
            companyId = Web3.toText(transaction[3]).strip('\x00')  # Adjust the index based on struct

            transactions.append({
                "id": transaction[0],
                "dataHash": transaction[1],
                "isFraudulent": transaction[2],
                "companyId": companyId
            })

        return {"success": True, "transactions": transactions}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

# MongoDB Connection and Smart Contract Initialization
def connectDB():
    from pymongo import MongoClient
    global transactionsCollection, companiesCollection, contract, web3
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client['your_database_name']  # Replace with your database name
    transactionsCollection = db['transactions']
    companiesCollection = db['companies']
    print("Connected to MongoDB")

    # Initialize Web3
    NETWORK_URL = os.getenv("NETWORK_URL")
    web3 = Web3(Web3.HTTPProvider(NETWORK_URL))
    if not web3.isConnected():
        print(f"Failed to connect to Ethereum node at {NETWORK_URL}")
        sys.exit(1)
    print(f"Connected to Ethereum node at {NETWORK_URL}")

    # Load contract ABI
    contract_json_path = Path(__file__).resolve().parent.parent / 'artifacts' / 'contracts' / 'SimpleFraudDetection.sol' / 'SimpleFraudDetection.json'
    with open(contract_json_path, 'r') as f:
        contract_json = json.load(f)
    contract_abi = contract_json['abi']

    # Environment variables
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

    # Contract instance
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
    print(f"Connected to smart contract at {CONTRACT_ADDRESS}")

# Start server
if __name__ == "__main__":
    import uvicorn
    load_ethereum_addresses()
    load_company_address_map()
    connectDB()
    uvicorn.run(app, host="0.0.0.0", port=3001)
