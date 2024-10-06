# API Documentation

## 1. Train Model
Train the fraud detection model using transaction data.

URL: /train
Method: POST
Content-Type: multipart/form-data (*optional*)

### CSV Format

The columns should be `Date,Time,Name,Amount,Location,Zip,Balance,Fraud`

Example:

```
2012-01-01,09:00:00,Rent,-960.0,Oviedo FL,32765,7040.0,0
```

### The Response

```
{
  "message": "Your own personal model has been trained to your habits!"
}
```

## 2. Predict Fraud

Predict the probability of fraud for a single transaction.

URL: /predict
Method: POST
Content-Type: application/json

### Request Body
```
{
  "transaction": {
    "DateTime": "2024-7-12 22:30:00",
    "Name": "Wawa",
    "Amount": 12,
    "Location": "Atlanta GA",
    "Zip": 30303,
    "Balance": 9800
},
```

### Response
```
{
    "fraud_probability": 0.4456
}
```