import sys
import os
from pathlib import Path
import requests
import json


# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
from app.models.fraud_model import process_data, train_model, predict_fraud_probability
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/train")
async def train_model_endpoint(file: UploadFile = File(None)):
    global model, X, user_details, scaler, usual_hour, hour_tolerance, usual_locations, amount_stats
    
    if file:
        file_location = f"data/{file.filename}"
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
    
    if model is None:
        raise HTTPException(status_code=400, detail="Model not trained. Please train the model first.")
    
    transaction_dict = transaction.model_dump()

    probability = predict_fraud_probability(transaction_dict, X, model, scaler, user_details, usual_hour, hour_tolerance, usual_locations, amount_stats)

    is_fraud = 1 if probability > 0.4 else 0

    transaction_data = {
        "transactionId": transaction_counter,
        "companyId": transaction.Name,
        "sender": "0x22D50A97397A307952Ba2f54Ab5eAA7f6a993De2",
        "receiver": "0x5Dc4F732052b3272e9a157B00C4A85C07E554340",
        "isFraudulent": is_fraud,
        "amount": transaction.Amount,
        "timestamp": transaction.DateTime
    }
    json_data = json.dumps(transaction_data)

    response = requests.post(
        "http://localhost:3001/record-transaction",
        data=json_data,
        headers = {
            "Content-Type": "application/json"
        }
    )

    if response.status_code == 200:
        print("It's public on the blockchain!")
        print("Response:", response.json())

    transaction_counter += 1

    return {"fraud_probability": probability}

