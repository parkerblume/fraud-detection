// backend/db.js
require('dotenv').config();
const { MongoClient } = require('mongodb');

const uri = process.env.MONGODB_URI;

// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(uri);

async function connectDB() {
  try {
    // Connect the client to the server (optional starting in v4.7)
    await client.connect();
    console.log('Connected to MongoDB Atlas');
  } catch (error) {
    console.error('Error connecting to MongoDB Atlas:', error);
  }
}

// Export the client and collections
const db = client.db('fraud_detection');
const transactionsCollection = db.collection('transactions');
const companiesCollection = db.collection('companies');

module.exports = {
  connectDB,
  client,
  transactionsCollection,
  companiesCollection,
};
