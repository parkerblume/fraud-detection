// readLedger.js
require('dotenv').config();
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Load contract ABI
const contractJson = JSON.parse(
  fs.readFileSync(
    path.resolve(__dirname, '../artifacts/contracts/SimpleFraudDetection.sol/SimpleFraudDetection.json'),
    'utf8'
  )
);
const contractAbi = contractJson.abi;

// Environment variables
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;
const NETWORK_URL = process.env.NETWORK_URL;

// Set up provider and signer
const provider = new ethers.providers.JsonRpcProvider(NETWORK_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

// Contract instance
const contract = new ethers.Contract(CONTRACT_ADDRESS, contractAbi, wallet);

async function readLedger() {
  try {
    const transactionCount = await contract.transactionCount();
    const count = transactionCount.toNumber();

    console.log(`Total Transactions: ${count}\n`);

    for (let i = 1; i <= count; i++) {
      const transaction = await contract.transactions(i);

      console.log(`Transaction ID: ${transaction.id.toString()}`);
      console.log(`Data Hash: ${transaction.dataHash}`);
      console.log(`Is Fraudulent: ${transaction.isFraudulent}`);
      console.log('---------------------------------------');
    }
  } catch (error) {
    console.error('Error reading ledger:', error);
  }
}

readLedger();
