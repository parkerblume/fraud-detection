// readLedger.js

require('dotenv').config();
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Load contract ABI
const contractJsonPath = path.resolve(__dirname, '../artifacts/contracts/SimpleFraudDetection.sol/SimpleFraudDetection.json');

if (!fs.existsSync(contractJsonPath)) {
  console.error(`Error: Contract ABI file not found at ${contractJsonPath}`);
  process.exit(1);
}

const contractJson = JSON.parse(fs.readFileSync(contractJsonPath, 'utf8'));
const contractAbi = contractJson.abi;

// Environment variables
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;
const NETWORK_URL = process.env.NETWORK_URL;

// Validate environment variables
if (!PRIVATE_KEY || !CONTRACT_ADDRESS || !NETWORK_URL) {
  console.error('Error: Missing required environment variables. Please check your .env file.');
  process.exit(1);
}

// Set up provider and signer
const provider = new ethers.providers.JsonRpcProvider(NETWORK_URL);
// For read-only operations, signer is not necessary. You can omit the wallet.
const contract = new ethers.Contract(CONTRACT_ADDRESS, contractAbi, provider);

// Load company-address mapping
const companyAddressMapFile = path.resolve(__dirname, '../../app/company_address_map.json');
let companyAddressMap = {};

// Function to load company-address mappings
function loadCompanyAddressMap() {
  if (fs.existsSync(companyAddressMapFile)) {
    try {
      const data = fs.readFileSync(companyAddressMapFile, 'utf8');
      companyAddressMap = JSON.parse(data);
      console.log(`Loaded company-address mappings for ${Object.keys(companyAddressMap).length} companies.`);
    } catch (error) {
      console.error(`Error reading ${companyAddressMapFile}:`, error);
      process.exit(1);
    }
  } else {
    console.warn(`Warning: ${companyAddressMapFile} not found. Sender addresses will be marked as 'N/A'.`);
    companyAddressMap = {};
  }
}

// Initialize company-address mapping
loadCompanyAddressMap();

// Function to decode bytes32 to string
function decodeBytes32(bytes32String) {
  try {
    return ethers.utils.parseBytes32String(bytes32String);
  } catch (error) {
    console.error('Error decoding bytes32 string:', error);
    return 'InvalidCompanyID';
  }
}

async function readLedger() {
  try {
    const transactionCount = await contract.transactionCount();
    const count = transactionCount.toNumber();

    console.log(`Total Transactions: ${count}\n`);

    for (let i = 1; i <= count; i++) {
      const transaction = await contract.transactions(i);

      const transactionId = transaction.id.toString();
      const dataHash = transaction.dataHash;
      const isFraudulent = transaction.isFraudulent;
      const companyIdBytes32 = transaction.companyId;
      const companyId = decodeBytes32(companyIdBytes32);

      // Fetch sender address from the mapping
      const senderAddress = companyAddressMap[companyId] || 'N/A';

      console.log(`Transaction ID: ${transactionId}`);
      console.log(`Data Hash: ${dataHash}`);
      console.log(`Is Fraudulent: ${isFraudulent}`);
      console.log(`Company ID: ${companyId}`);
      console.log(`Sender Address: ${senderAddress}`);
      console.log('---------------------------------------');
    }
  } catch (error) {
    console.error('Error reading ledger:', error);
  }
}

readLedger();