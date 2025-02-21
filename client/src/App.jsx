// App.jsx
import React, { useState, useRef } from 'react';
import { Upload, Play, AlertTriangle, Loader, StopCircle } from 'lucide-react';
import Papa from 'papaparse';

const Alert = ({ children, type = 'info' }) => {
  const colors = {
    info: 'bg-blue-100 border-blue-500 text-blue-700',
    success: 'bg-green-100 border-green-500 text-green-700',
    error: 'bg-red-100 border-red-500 text-red-700',
  };
  return (
    <div className={`${colors[type]} border-l-4 p-4 mt-4`} role="alert">
      <p className="font-bold">{type.charAt(0).toUpperCase() + type.slice(1)}</p>
      <p>{children}</p>
    </div>
  );
};

const FraudDetectionDashboard = () => {
  const [trainFile, setTrainFile] = useState(null);
  const [simulationData, setSimulationData] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingMessage, setTrainingMessage] = useState('');
  const [csvInput, setCsvInput] = useState('');
  const [simulationStatus, setSimulationStatus] = useState('');
  const trainFileInputRef = useRef(null);
  const isSimulatingRef = useRef(false);
  const [ledger, setLedger] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchLedger = async () => {
    try {
      setLedger([]);  // Clear the ledger before fetching new data
      const response = await fetch('http://localhost:3001/ledger');
      const data = await response.json();
      if (data.success) {
        // Ensure no duplicate entries before setting the ledger
        const uniqueLedger = data.ledger.filter((entry, index, self) =>
          index === self.findIndex((t) => t.transactionId === entry.transactionId)
        );
        setLedger(uniqueLedger);
        setIsModalOpen(true);
      } else {
        console.error('Failed to fetch ledger');
      }
    } catch (error) {
      console.error('Error fetching ledger:', error);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const handleTrainFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setTrainFile(file);
      setIsTraining(true);
      setTrainingMessage('');
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await fetch('http://127.0.0.1:8000/train', {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        setTrainingMessage(data.message);
      } catch (error) {
        console.error('Error training model:', error);
        setTrainingMessage('Error training model. Please try again.');
      } finally {
        setIsTraining(false);
      }
    }
  };

  const handleCsvInputChange = (event) => {
    setCsvInput(event.target.value);
  };

  const parseManualCsvInput = () => {
    const { data } = Papa.parse(csvInput, { header: true, skipEmptyLines: true });
    setSimulationData(data);
    console.log('Parsed simulation data:', data);
    setSimulationStatus(`Parsed ${data.length} transactions`);
  };

  const simulateTransactions = async () => {
    console.log('Starting simulation...');
    if (simulationData.length === 0) {
      alert('Simulation data is not available. Please input CSV data and parse it first.');
      return;
    }
    setIsSimulating(true);
    isSimulatingRef.current = true;
    setTransactions([]);
    setSimulationStatus('Simulation in progress...');
    console.log(`Simulation data length: ${simulationData.length}`);

    for (let i = 0; i < simulationData.length; i++) {
      if (!isSimulatingRef.current) {
        console.log('Simulation stopped.');
        break;
      }

      const row = simulationData[i];
      const dateTime = `${row.Date} ${row.Time}`;
      const transaction = {
        DateTime: dateTime,
        Name: row.Name,
        Amount: parseFloat(row.Amount),
        Location: row.Location,
        Zip: row.Zip,
        Balance: parseFloat(row.Balance),
      };

      console.log(`Processing transaction ${i + 1}/${simulationData.length}:`, transaction);
      setTransactions(prev => [...prev, { ...transaction, status: 'pending' }]);

      try {
        const response = await fetch('http://127.0.0.1:8000/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(transaction),
        });
        const { fraud_probability } = await response.json();
        console.log(`Fraud probability for transaction ${i + 1}: ${fraud_probability}`);
        setTransactions(prev =>
          prev.map((t, index) =>
            index === prev.length - 1 ? { ...t, fraud_probability, status: 'complete' } : t
          )
        );
      } catch (error) {
        console.error('Error predicting fraud:', error);
      }

      setSimulationStatus(`Processed ${i + 1}/${simulationData.length} transactions`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
    }

    setIsSimulating(false);
    isSimulatingRef.current = false;
    setSimulationStatus('Simulation completed');
    console.log('Simulation finished.');
  };

  const stopSimulation = () => {
    console.log('Stopping simulation...');
    setIsSimulating(false);
    isSimulatingRef.current = false;
  };

  const getFraudSeverity = (probability) => {
    if (probability > 0.8) return 'high';
    if (probability > 0.6) return 'medium';
    if (probability > 0.5) return 'low';
    return 'none';
  };

  const severityColor = {
    high: 'bg-red-100',
    medium: 'bg-yellow-100',
    low: 'bg-blue-100',
    none: '',
  };

  const severityIconColor = {
    high: 'text-red-500',
    medium: 'text-yellow-500',
    low: 'text-blue-500',
  };

  return (
    <div className="p-4">
      {/* Training and Simulation Controls */}
      <div className="mb-4 flex space-x-4">
        <button
          onClick={() => trainFileInputRef.current.click()}
          disabled={isTraining}
          className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center ${
            isTraining && 'opacity-50 cursor-not-allowed'
          }`}
        >
          {isTraining ? <Loader className="mr-2 animate-spin" size={20}/> : <Upload className="mr-2" size={20}/>}
          {isTraining ? 'Training...' : 'Upload Train CSV'}
        </button>
        <input
          type="file"
          ref={trainFileInputRef}
          onChange={handleTrainFileUpload}
          accept=".csv"
          className="hidden"
        />
        <button
          onClick={simulateTransactions}
          disabled={isSimulating || simulationData.length === 0 || isTraining}
          className={`px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 flex items-center ${
            (isSimulating || simulationData.length === 0 || isTraining) && 'opacity-50 cursor-not-allowed'
          }`}
        >
          <Play className="mr-2" size={20}/>
          {isSimulating ? 'Simulating...' : 'Start Simulation'}
        </button>
        <button
          onClick={stopSimulation}
          disabled={!isSimulating}
          className={`px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 flex items-center ${
            !isSimulating && 'opacity-50 cursor-not-allowed'
          }`}
        >
          <StopCircle className="mr-2" size={20}/>
          Stop Simulation
        </button>
      </div>

      {/* Training Alerts */}
      {isTraining && (
        <Alert>
          Please wait while your model learns from your data...
        </Alert>
      )}
      {trainingMessage && (
        <Alert type="success">
          {trainingMessage}
        </Alert>
      )}

      {/* CSV Input */}
      <div className="mt-4">
        <h3 className="text-lg font-semibold mb-2">Input CSV Data</h3>
        <textarea
          value={csvInput}
          onChange={handleCsvInputChange}
          className="w-full h-40 p-2 border rounded"
          placeholder="Paste your CSV data here..."
        />
        <button
          onClick={parseManualCsvInput}
          className="mt-2 px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
        >
          Parse CSV Input
        </button>
      </div>

      {/* Simulation Status Alert */}
      {simulationStatus && (
        <Alert type="info">
          {simulationStatus}
        </Alert>
      )}

      {/* Transactions Table */}
      <div className="border rounded-lg overflow-hidden mt-4">
        <div className="max-h-96 overflow-y-auto text-black">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left">Date Time</th>
                <th className="px-4 py-2 text-left">Name</th>
                <th className="px-4 py-2 text-left">Amount</th>
                <th className="px-4 py-2 text-left">Location</th>
                <th className="px-4 py-2 text-left">Zip</th>
                <th className="px-4 py-2 text-left">Balance</th>
                <th className="px-8 py-2 text-left">Alert</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction, index) => {
                const severity = transaction.status === 'complete' ? getFraudSeverity(transaction.fraud_probability) : 'none';
                return (
                  <tr key={index} className={`${severityColor[severity]} ${transaction.status === 'pending' ? 'animate-pulse' : ''}`}>
                    <td className="px-4 py-2">{transaction.DateTime}</td>
                    <td className="px-4 py-2">{transaction.Name}</td>
                    <td className="px-4 py-2">${transaction.Amount.toFixed(2)}</td>
                    <td className="px-4 py-2">{transaction.Location}</td>
                    <td className="px-4 py-2">{transaction.Zip}</td>
                    <td className="px-4 py-2">${transaction.Balance.toFixed(2)}</td>
                    <td className="px-4 py-2 relative group">
                      {transaction.status === 'complete' ? (
                        <>
                          {severity !== 'none' && (
                            <div className="absolute top-1/2 right-2 transform -translate-y-1/2">
                              <AlertTriangle
                                size={20}
                                className={`${severityIconColor[severity]}`}
                              />
                              <div
                                className="invisible group-hover:visible absolute z-10 w-48 text-sm bg-gray-800 text-white rounded p-2 right-0 bottom-full mb-2">
                                Fraud Severity: {severity.charAt(0).toUpperCase() + severity.slice(1)}
                              </div>
                            </div>
                          )}
                        </>
                      ) : (
                        'Pending...'
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ledger Modal */}
      <div className="p-4">
        <button onClick={fetchLedger} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          Show Ledger
        </button>

        {isModalOpen && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center text-black">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h2 className="text-lg font-semibold mb-4">Ledger</h2>
              <div className="max-h-96 overflow-y-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr>
                      <th className="border-b px-4 py-2">Transaction ID</th>
                      <th className="border-b px-4 py-2">Data Hash</th>
                      <th className="border-b px-4 py-2">Is Fraudulent</th>
                      <th className="border-b px-4 py-2">Company ID</th>
                      <th className="border-b px-4 py-2">Sender Address</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ledger.map((transaction, index) => (
                      <tr key={index}>
                        <td className="border-b px-4 py-2">{transaction.transactionId}</td>
                        <td className="border-b px-4 py-2">{transaction.dataHash}</td>
                        <td className="border-b px-4 py-2">{transaction.isFraudulent ? 'Yes' : 'No'}</td>
                        <td className="border-b px-4 py-2">{transaction.companyId}</td>
                        <td className="border-b px-4 py-2">{transaction.senderAddress}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <button onClick={closeModal} className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">
                Close
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
};

export default FraudDetectionDashboard;
