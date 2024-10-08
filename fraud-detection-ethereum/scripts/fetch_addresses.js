// fetch_addresses.js

const { ethers } = require('ethers');
const fs = require('fs');

// Configuration
const NETWORK_URL = 'http://localhost:8545';
const OUTPUT_FILE = 'ethereum_addresses.txt';

async function fetchAddresses() {
    try {
        // Connect to the Ethereum provider (Ganache)
        const provider = new ethers.providers.JsonRpcProvider(NETWORK_URL);

        // Fetch all accounts
        const accounts = await provider.listAccounts();

        if (accounts.length === 0) {
            console.log('No accounts found.');
            return;
        }

        // Write addresses to the output file
        fs.writeFileSync(OUTPUT_FILE, accounts.join('\n'), 'utf8');
        console.log(`Ethereum addresses have been saved to ${OUTPUT_FILE}`);
    } catch (error) {
        console.error('Error fetching addresses:', error);
    }
}

fetchAddresses();
