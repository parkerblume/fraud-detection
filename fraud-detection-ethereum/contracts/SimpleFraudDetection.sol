// contracts/SimpleFraudDetection.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleFraudDetection {
    struct TransactionRecord {
    uint256 id;
    bytes32 dataHash;
    bool isFraudulent;
    bytes32 companyId;
}


    uint256 public transactionCount;
    mapping(uint256 => TransactionRecord) public transactions;

    event TransactionRecorded(uint256 indexed id, bytes32 dataHash, bool isFraudulent, bytes32 companyId);


    event FraudFlagged(
        uint256 indexed id
    );

    // Record a transaction's hash on-chain
    function recordTransaction(bytes32 _dataHash, bool _isFraudulent, bytes32 _companyId) public {
        transactionCount++;
        transactions[transactionCount] = TransactionRecord(
            transactionCount,
            _dataHash,
            _isFraudulent,
            _companyId
        );
        emit TransactionRecorded(transactionCount, _dataHash, _isFraudulent, _companyId);
    }


    // Flag a transaction as fraudulent
    function flagFraud(uint256 _transactionId) public {
        require(_transactionId > 0 && _transactionId <= transactionCount, "Invalid transaction ID");
        transactions[_transactionId].isFraudulent = true;
        emit FraudFlagged(_transactionId);
    }

    // Verify the hash of off-chain data
    function verifyTransaction(uint256 _transactionId, bytes32 _dataHash) public view returns (bool) {
        return transactions[_transactionId].dataHash == _dataHash;
    }
}
