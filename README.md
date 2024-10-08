# CreditShield

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![Issues](https://img.shields.io/github/issues/noway-code/CreditShield.svg)](https://github.com/parkerblume/fraud-detection/issues)  
[![Forks](https://img.shields.io/github/forks/noway-code/CreditShield.svg)](https://github.com/parkerblume/fraud-detection/network)  
[![Stars](https://img.shields.io/github/stars/noway-code/CreditShield.svg)](https://github.com/parkerblume/fraud-detection/stargazers)

## Overview
CreditShield is a machine learning-powered fraud detection system that uses synthetic data and blockchain technology to ensure data integrity and scalability. It monitors real-time transactions in bank accounts, identifies potential fraudulent activity, and provides secure ledger management via blockchain. The system integrates a real-time data stream using Apache Kafka and Ethereum blockchain for secure and decentralized ledgering.

## Features
- **Machine Learning Model**: Trained on synthetic data to detect fraudulent transactions.
- **Blockchain Integration**: Uses Ethereum for secure, decentralized, and scalable ledger management.
- **Real-time Data Streaming**: Implements Apache Kafka for real-time transaction processing.
- **Synthetic Data Generation**: Generates realistic data for model training.
- **User-friendly Interface**: Clean and intuitive UI for interaction.

## Table of Contents
- [Inspiration](#inspiration)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [Accomplishments](#accomplishments)
- [What We Learned](#what-we-learned)
- [Future Plans](#future-plans)
- [Built With](#built-with)
- [Contributing](#contributing)
- [License](#license)
- [Try It Out](#try-it-out)

## Inspiration
BNY's challenge caught our attention because of the rising importance of technology in fraud prevention. Integrating AI and real-time data processing into systems that protect people is essential, and this project aimed to address that.

## Installation

### Prerequisites
- Python 3.8+
- Node.js
- Apache Kafka
- MongoDB
- Ethereum client (e.g., Geth or Infura)
- Solidity compiler

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
   npx hardhat compile
   npx hardhat run ../scripts/deploy.js --network localhost
   ```
    Copy the string in the terminal and add it to the `.env` for <CONTRACT_ADDRESS>.
   ```bash
   cd backend
   node index.js
   ```
6. In a new terminal run: ``node fraud-detection-ethereum/scripts/fetch_addresses.js``

7. Run the backend services:
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

## Usage

After completing the setup:
1. Access the front-end at `http://localhost:5173/`.
2. First train the model by uploading a CSV file with transaction data (use the `transactions.csv` file in the `data` directory).
3. When the model is trained, you can start the real-time data stream by pasting in. You can copy the data from the `client/src/assets/real_time_transactions.csv`file.
4. Verify the blockchain at anytime by running `cd fraud-detection-ethereum/backend` and `node readLedger.js`.

## How We Built It

Our team divided the project into four main components:
- **Machine Learning Model**: Developed using Python, Pandas, and Scikit-learn, trained on synthetic data generated for fraud detection.
- **Blockchain Integrity**: Implemented Ethereum-based ledgering using Solidity smart contracts to ensure transaction integrity.
- **Real-time Data Stream**: Leveraged Apache Kafka and Zookeeper for real-time transaction streaming.
- **Frontend**: Built using React and TailwindCSS for a responsive and clean user interface.

## Challenges We Faced

One of the major challenges was aligning the different parts of the project, especially since we didn't start with a fully defined plan. Early on, much of the work was done individually, and integrating these pieces was challenging but rewarding.

## Accomplishments

- **Model Accuracy**: We successfully trained a machine learning model that provides accurate fraud predictions while avoiding overfitting.
- **Synthetic Data Generation**: Created a complex system to generate realistic synthetic data for training the model.
- **Blockchain Ledger**: Deployed a secure and decentralized ledger using Ethereum smart contracts.

## What We Learned

Key takeaways include:
- The importance of clear planning and communication.
- Hands-on experience with machine learning and synthetic data generation.
- Introduction to real-time data processing using Apache Kafka.
- Gained experience with blockchain and Solidity smart contract development.

## Future Plans
We are proud of what we achieved during the development of CreditShield. While there are no immediate plans for further work, we’re excited to continue exploring the concepts and technologies we worked with, especially in future projects.

## Built With

- **AI/ML**: Python, Pandas, Scikit-learn, NumPy
- **Blockchain**: Ethereum, Solidity, Geth, Infura
- **Real-time Streaming**: Apache Kafka, Zookeeper
- **Frontend**: React, TailwindCSS
- **Backend**: Flask
- **Database**: MongoDB

## Contributing

We welcome contributions! Feel free to submit a pull request or open an issue to discuss any changes or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Try It Out

Try out CreditShield for real-time fraud detection using machine learning and blockchain technology.

--- 
**Note**: If you want to contribute or try out the code, check the repository and follow the [installation](#installation) instructions.    

## To run server
With the environment activated, run `uvicorn main:app --reload`