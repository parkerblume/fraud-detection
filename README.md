# CreditShield - BNY Mellon Fraud Detection Challenge

CreditShield was developed during the **KnightHacks 7 Hackathon** in response to a fraud detection challenge sponsored by **BNY Mellon**. This project leverages machine learning, real-time transaction analysis, and blockchain technology to detect and manage suspicious financial activities.

## 🏆 Awarded **1st place for BNY Mellon challenge**. 🏆

## Table of Contents
- [Problem Statement](#problem-statement)
- [Our Solution](#our-solution)
  - [Synthetic Data Generation](#synthetic-data-generation)
  - [The Model](#the-model)
  - [The Frontend](#the-frontend)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [Accomplishments](#accomplishments)
- [What We Learned](#what-we-learned)
- [Future Plans](#future-plans)
- [Built With](#built-with)
- [Team](#team)
- [License](#license)

## Problem Statement

Financial fraud, including identity theft and transaction fraud, remains a persistent challenge in the banking sector. The goal is to develop an AI model that analyzes real-time transactions to detect suspicious activity. Utilizing historical transaction data and patterns, the objective is to build a machine learning model that flags anomalies effectively.

## Our Solution

**CreditShield** is a machine learning-powered fraud detection system that employs synthetic data and blockchain technology to ensure data integrity and scalability. It monitors real-time transactions in bank accounts, identifies potential fraudulent activities, and provides secure ledger management via blockchain. The system integrates a real-time data stream using Apache Kafka and leverages the Ethereum blockchain for secure and decentralized ledgering.

### Synthetic Data Generation

Due to the sensitive nature of bank statements, acquiring real datasets is challenging. To address this, we developed a synthetic data generation script that creates realistic transaction data for training our model. This synthetic data simulates typical transaction patterns of individuals by incorporating various features that influence spending behavior.

### The Model

We implemented a **Random Forest Classification Model** for its effectiveness in identifying outliers and anomalies within datasets, making it well-suited for predicting potential fraudulent purchases.

Using the synthetic data, the model was trained to recognize individual spending patterns based on various features:

- **Geographical Data**: Cities where frequent purchases occur.
- **Temporal Patterns**: Typical times and days of transactions.
- **Transaction Amount**: The amount involved in each purchase.
- **Demographic Information**: Credit score and age (to introduce bias).

Additional engineered features enhance the model’s ability to detect unusual patterns:

- **Day of the Week**: Flexibility to account for higher spending on specific days (e.g., Saturdays vs. Tuesdays).
- **Unusual Purchase Times**: Transactions occurring at atypical hours.
- **Spending Amount Analysis**: Using Z-scores to evaluate the amount spent within specific hours.

### The Frontend

Given the two-hour time constraint of the hackathon, the frontend was designed to be simple yet functional. It allows users to upload a bank statement in `.csv` format, which is then sent to the backend Python server to train the model on the user's purchase patterns.

Additionally, the frontend simulates real-time transactions, where the model assigns a probability to each transaction. Based on these probabilities, transactions are classified as:

- **Low Risk**: 40-60%
- **Medium Risk**: 60-80%
- **High Risk**: >80%

## Installation

### Prerequisites
Ensure you have the following installed on your system:

- **Python**: Version 3.8 or higher
- **Node.js**: Latest LTS version recommended
- **Apache Kafka**: For real-time data streaming
- **MongoDB**: Database for storing transaction data
- **Ethereum Client**: Ganache CLI for local blockchain deployment
- **Solidity Compiler**: For smart contract deployment

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/noway-code/CreditShield.git
   cd CreditShield
   ```

2. Install the Python and Node.js dependencies:
   ```bash
   python -m venv myenv
   ```
   Run:

    On Windows: `myenv\Scripts\Activate`

    On Linux: `source myenv/bin/activate`
    ```bash
   pip install -r requirements.txt
   ```
   
3. Start the Ethereum client:
   ```bash
   cd fraud-detection-etehereum
   npm install
   npm install -g ganache-cli
   ganache-cli --gasPrice 0 --defaultBalanceEther 1000000 --accounts 1000

4. Run the backend and frontend services:

    In a new terminal:
   ```bash
   cd backend
   npm install
   touch .env
   ```
    
    Add the following environment variables to the `.env` file:

   ```bash
   NETWORK_URL=http://localhost:8545
   MONGODB_URI=<your_mongodb_uri>
   PRIVATE_KEY=<your_private_key>
   CONTRACT_ADDRESS=<your_contract_address>
   ```
   - MongoDB: Go to the MongoDB Atlas website and create a new cluster. Add your IP to the database connections. Get the mongo connection string with username and password add it to the `.env` for <MONGO_URI>.
   - Find ganache-cli, choose any of the private keys and add it to the `.env` for <private_key>.
5. In a new terminal compile and deploy the smart contract:
   ```bash
   cd fraud-detection-ethereum/
   npx hardhat compile
   npx hardhat run scripts/deploy.js --network localhost
   ```
    Copy the string in the terminal and add it to the `.env` for <CONTRACT_ADDRESS>.
   ```bash
   cd backend
   node index.js
   ```
6. In a new terminal run: ``node fraud-detection-ethereum/scripts/fetch_addresses.js``

7. Run the backend services in your python environment:
   ```bash
   cd app
   uvicorn main:app --reload
   ```
   
8. In a new terminal, start the frontend:
   ```bash
   cd client
   npm install
   npm run dev
   ```

After completing the setup, follow these steps to use CreditShield:

1. **Access the Frontend**
   Open your browser and navigate to [http://localhost:5173/](http://localhost:5173/).

2. **Train the Model**
   Upload a CSV file containing transaction data (use the provided `transactions.csv` file in the `data` directory).

3. **Simulate Real-Time Transactions**
   Start the real-time data stream by uploading data from `client/src/assets/real_time_transactions.csv`.

4. **Verify the Blockchain**
   At any time, verify the blockchain ledger by running:
   ```bash
   cd fraud-detection-ethereum/backend
   node readLedger.js
   ```

## How We Built It

The project was divided into four main components:

- **Machine Learning Model**: Developed using Python, Pandas, and Scikit-learn, trained on synthetic data for fraud detection.
- **Blockchain Integrity**: Implemented Ethereum-based ledgering using Solidity smart contracts to ensure transaction integrity.
- **Real-Time Data Stream**: Leveraged Apache Kafka and Zookeeper for real-time transaction streaming.
- **Frontend**: Built using React and TailwindCSS for a responsive and clean user interface.

## Challenges We Faced

One of the major challenges was integrating the different components of the project, especially without a fully defined initial plan. Much of the work was done individually, making the integration process both challenging and rewarding.

## Accomplishments

- **Model Accuracy**: Successfully trained a machine learning model that provides accurate fraud predictions while avoiding overfitting.
- **Synthetic Data Generation**: Developed a system to generate realistic synthetic data for effective model training.
- **Blockchain Ledger**: Deployed a secure and decentralized ledger using Ethereum smart contracts.

## What We Learned

Key takeaways from the project include:

- The importance of clear planning and effective communication.
- Hands-on experience with machine learning and synthetic data generation.
- Introduction to real-time data processing using Apache Kafka.
- Gained proficiency in blockchain technology and Solidity smart contract development.

## Future Plans

We are proud of our achievements with CreditShield. While there are no immediate plans for further development, we are excited to continue exploring the concepts and technologies we worked with in future projects.

## Built With

- **AI/ML**: Python, Pandas, Scikit-learn, NumPy
- **Blockchain**: Ethereum, Solidity, Geth, Infura
- **Real-Time Streaming**: Apache Kafka, Zookeeper
- **Frontend**: React, TailwindCSS
- **Backend**: FastAPI, Flask
- **Database**: MongoDB

## Team

- [Parker Blume](https://github.com/parkerblume/)
- [Garrison Scarboro](https://github.com/gscarboro)
- [Darren Bansil](https://github.com/libioco)
- [Camilo Alvarez-Velez](https://github.com/noway-code)

## License

This project is licensed under the **GPLv3 License** - see the [LICENSE](LICENSE) file for details.