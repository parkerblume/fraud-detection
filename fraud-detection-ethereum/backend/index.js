// backend/index.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { ethers } = require('ethers');
const fs = require('fs');
const crypto = require('crypto');
const { connectDB, transactionsCollection, companiesCollection } = require('./db');``

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const NETWORK_URL = process.env.NETWORK_URL;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;

const path = require('path');
const contractJson = JSON.parse(
  fs.readFileSync(
    path.resolve(__dirname, '../artifacts/contracts/SimpleFraudDetection.sol/SimpleFraudDetection.json'),
    'utf8'
  )
);
const contractAbi = contractJson.abi;

function stringToBytes32(str) {
  return ethers.utils.formatBytes32String(str);
}

// Connect to local network
const provider = new ethers.providers.JsonRpcProvider(NETWORK_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

// Create contract instance
const contract = new ethers.Contract(CONTRACT_ADDRESS, contractAbi, wallet);

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 3001;

// Function to hash transaction data
const stringify = require('json-stable-stringify');

function hashTransactionData(transactionData) {
    const dataString = stringify(transactionData);
    return crypto.createHash('sha256').update(dataString).digest('hex');
}

app.post('/record-transaction', async (req, res) => {
  const transactionData = req.body;
  const { isFraudulent = false } = transactionData;

  try {
    // Generate data hash
    const dataHash = hashTransactionData(transactionData);

    // Add hash to transaction data
    transactionData.dataHash = dataHash;

    // Save transaction data to MongoDB
    await transactionsCollection.insertOne(transactionData);

    // Update company's transaction counts
    const companyId = transactionData.companyId;
    const updateFields = {
      $inc: { totalTransactions: 1 },
      $setOnInsert: {
        companyId: companyId,
      },
    };

    if (isFraudulent) {
      updateFields.$inc.fraudulentTransactions = 1;
    }

    const options = {
      returnDocument: 'after',
      upsert: true,
    };

    const updatedCompany = await companiesCollection.findOneAndUpdate(
      { companyId: companyId },
      updateFields,
      options
    );

    if (!updatedCompany.value) {
      // Fetch the document if value is null
      const companyDoc = await companiesCollection.findOne({ companyId: companyId });
      if (!companyDoc) {
        return res.status(500).send({ success: false, message: 'Error retrieving company data' });
      }
      updatedCompany.value = companyDoc;
    }

    // Calculate new risk score
    const totalTransactions = updatedCompany.value.totalTransactions || 1;
    const fraudulentTransactions = updatedCompany.value.fraudulentTransactions || 0;
    const riskScore = (fraudulentTransactions / totalTransactions) * 100;

    // Update risk score
    await companiesCollection.updateOne(
      { companyId: companyId },
      { $set: { riskScore: riskScore } }
    );

    // Convert companyId to bytes32
    const companyIdBytes32 = stringToBytes32(companyId);

    // Record transaction on blockchain
    const tx = await contract.recordTransaction(`0x${dataHash}`, isFraudulent, companyIdBytes32);
    await tx.wait();

    res.status(200).send({ success: true, txHash: tx.hash });
  } catch (error) {
    console.error('Error recording transaction:', error);
    res.status(500).send({ success: false, error: error.message });
  }
});

app.get('/companies/:companyId', async (req, res) => {
  const { companyId } = req.params;

  try {
    const company = await companiesCollection.findOne({ companyId });
    if (!company) {
      return res.status(404).send({ success: false, message: 'Company not found' });
    }
    res.status(200).send({ success: true, company });
  } catch (error) {
    console.error('Error retrieving company profile:', error);
    res.status(500).send({ success: false, error: error.message });
  }
});

app.get('/get-transaction/:transactionId', async (req, res) => {
  const { transactionId } = req.params;

  try {
    // Get transaction from smart contract
    const transaction = await contract.transactions(transactionId);

    // Format the data
    const transactionData = {
      id: transaction.id.toString(),
      dataHash: transaction.dataHash,
      isFraudulent: transaction.isFraudulent,
    };

    res.status(200).send({ success: true, transaction: transactionData });
  } catch (error) {
    console.error('Error retrieving transaction:', error);
    res.status(500).send({ success: false, error: error.message });
  }
});

app.get('/get-transaction/:transactionId', async (req, res) => {
  const { transactionId } = req.params;

  try {
    // Get transaction from smart contract
    const transaction = await contract.transactions(transactionId);

    // Format the data
    const transactionData = {
      id: transaction.id.toString(),
      dataHash: transaction.dataHash,
      isFraudulent: transaction.isFraudulent,
    };

    res.status(200).send({ success: true, transaction: transactionData });
  } catch (error) {
    console.error('Error retrieving transaction:', error);
    res.status(500).send({ success: false, error: error.message });
  }
});

app.get('/get-all-transactions', async (req, res) => {
  try {
    const transactionCount = await contract.transactionCount();
    const count = transactionCount.toNumber();

    const transactions = [];

    for (let i = 1; i <= count; i++) {
      const transaction = await contract.transactions(i);

      transactions.push({
        id: transaction.id.toString(),
        dataHash: transaction.dataHash,
        isFraudulent: transaction.isFraudulent,
      });
    }

    res.status(200).send({ success: true, transactions });
  } catch (error) {
    console.error('Error retrieving transactions:', error);
    res.status(500).send({ success: false, error: error.message });
  }
});


connectDB();

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
