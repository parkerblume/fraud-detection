import React, {useState, useRef, useEffect} from 'react';
import {Upload, Play, AlertTriangle, Loader} from 'lucide-react';
import Papa from 'papaparse';

const Alert = ({children, type = 'info'}) => {
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
	const [errorMessage, setErrorMessage] = useState(''); // State to track errors
	const trainFileInputRef = useRef(null);
	const isSimulatingRef = useRef(isSimulating);

	useEffect(() => {
		isSimulatingRef.current = isSimulating;
	}, [isSimulating]);

	const handleTrainFileUpload = async (event) => {
		const file = event.target.files[0];
		if (file) {
			setTrainFile(file);
			setIsTraining(true);
			setTrainingMessage('');
			setErrorMessage('');
			const formData = new FormData();
			formData.append('file', file);
			try {
				const response = await fetch('http://127.0.0.1:8000/train', {
					method: 'POST',
					body: formData,
				});
				if (!response.ok) {
					throw new Error(`Error: ${response.status} ${response.statusText}`);
				}
				const data = await response.json();
				setTrainingMessage(data.message);
			} catch (error) {
				console.error('Error training model:', error);
				setErrorMessage(`Error training model: ${error.message}. Please try again.`);
			} finally {
				setIsTraining(false);
			}
		}
	};

	const handleCsvInputChange = (event) => {
		setCsvInput(event.target.value);
	};

	const parseManualCsvInput = () => {
		try {
			const {data, errors} = Papa.parse(csvInput, {header: true, skipEmptyLines: true});
			if (errors.length > 0) {
				throw new Error('CSV parsing error: ' + errors.map(err => err.message).join(', '));
			}
			setSimulationData(data);
			console.log('Parsed simulation data:', data); // Check that data is populated
		} catch (error) {
			console.error('Error parsing CSV input:', error);
			setErrorMessage(`Error parsing CSV input: ${error.message}.`);
		}
	};


	const simulateTransactions = async () => {
		console.log('Starting simulation...');

		// Ensure that simulation data exists
		if (simulationData.length === 0) {
			alert('Simulation data is not available. Please input CSV data and parse it first.');
			return;
		}

		setIsSimulating(true);
		isSimulatingRef.current = true; // Sync ref immediately
		setTransactions([]);
		setErrorMessage(''); // Clear any previous errors

		// Iterate through the simulation data
		for (const row of simulationData) {
			if (!isSimulatingRef.current) {
				console.log('Simulation stopped early'); // This will log if the simulation is stopped
				break;
			}

			console.log('Simulating transaction:', row);

			// Prepare the transaction object
			const dateTime = `${row.Date} ${row.Time}`;
			const transaction = {
				DateTime: dateTime,
				Name: row.Name,
				Amount: parseFloat(row.Amount),
				Location: row.Location,
				Zip: row.Zip,
				Balance: parseFloat(row.Balance),
			};

			// Add transaction with "pending" status
			setTransactions((prev) => [...prev, {...transaction, status: 'pending'}]);

			try {
				// Send POST request to the backend
				const response = await fetch('http://127.0.0.1:8000/predict', {
					method: 'POST',
					headers: {'Content-Type': 'application/json'},
					body: JSON.stringify(transaction),
				});

				// Check for response success
				if (!response.ok) {
					throw new Error(`Error: ${response.status} ${response.statusText}`);
				}

				// Parse the response
				const {fraud_probability} = await response.json();
				console.log('Fraud probability:', fraud_probability);

				// Update the transaction with the fraud probability
				setTransactions((prev) =>
					prev.map((t, index) =>
						index === prev.length - 1 ? {...t, fraud_probability, status: 'complete'} : t
					)
				);
			} catch (error) {
				console.error('Error predicting fraud:', error);
				setErrorMessage(`Error predicting fraud for transaction: ${transaction.Name}. ${error.message}`);
			}

			// Add a delay of 1 second
			await new Promise((resolve) => setTimeout(resolve, 1000));
		}

		// End simulation
		setIsSimulating(false);
		isSimulatingRef.current = false; // Sync ref immediately
		console.log('Simulation complete');
	};


	const stopSimulation = () => {
		setIsSimulating(false);
	};

	const getFraudSeverity = (probability) => {
		if (probability > 0.8) return 'high';
		if (probability > 0.60) return 'medium';
		if (probability > 0.50) return 'low';
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
					Stop Simulation
				</button>
			</div>
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
			{errorMessage && (
				<Alert type="error">
					{errorMessage}
				</Alert>
			)}
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
							<th className="px-4 py-2 text-left">Fraud Probability</th>
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
												{transaction.fraud_probability.toFixed(4)}
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
		</div>
	);
};

export default FraudDetectionDashboard;
