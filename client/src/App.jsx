import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';

function App() {
  const [counter, setCounter] = useState(1);
  const [transactions, setTransactions] = useState([]);
  const [prob, setProb] = useState();

  // Train the ML model on startup
  useEffect(() => {
    const trainModel = async () => {
      try {
        const fileResponse = await fetch('/transactions.csv');
        const fileBlob = await fileResponse.blob();

        const formData = new FormData();
        formData.append('file', fileBlob, 'transactions.csv');

        const response = await fetch('http://127.0.0.1:8000/train', {
          method: 'POST',
          body: formData,
        });
        if (response.ok) {
          console.log('Model trained successfully.');
        } else {
          console.error('Error training model:', response.statusText);
        }
      } catch (error) {
        console.error('Error during model training:', error);
      }
    };

    trainModel();
  }, []);

  const handleFetchAndParse = async () => {
    try {
      const response = await fetch('/transactions.csv');
      const csvText = await response.text();

      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        complete: async (results) => {
          // Select a random row based on the counter
          const randomRow = results.data[counter];
          setCounter((prevCounter) => prevCounter + 1);

          // Combine Date and Time into DateTime
          const dateTime = `${randomRow.Date} ${randomRow.Time}`;
          
          // Prepare the JSON payload
          const jsonPayload = {
            DateTime: dateTime,
            Name: randomRow.Name,
            Amount: randomRow.Amount,
            Location: randomRow.Location,
            Zip: randomRow.Zip,
            Balance: randomRow.Balance,
          };

          try {
            const response = await fetch('http://127.0.0.1:8000/predict', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(jsonPayload),
            });

            if (response.ok) {
              const jsonResponse = await response.json();
              const fraudProbability = jsonResponse.fraud_probability;
              
              // Add Fraud status to JSON payload based on the fraud probability
              jsonPayload.Fraud = fraudProbability > 0.4;

              console.log("prob: " + fraudProbability);

              // Add the transaction to the transactions state
              setTransactions((prevTransactions) => [...prevTransactions, jsonPayload]);
              setProb(fraudProbability);
            }
          } catch (error) {
            console.error('Error sending random row:', error);
          }
        },
      });
    } catch (error) {
      console.error('Error fetching CSV file:', error);
    }
  };

  return (
    <>
      <div className="flex flex-col w-full h-full p-3">
        <button onClick={handleFetchAndParse}>Simulate Transaction</button>
        <h1>Real-time Fraud Detection System</h1>
        <div className="flex flex-col text-black bg-white justify-center rounded-xl items-stretch p-3">
          <table>
            <thead>
              <tr>
                <th className="py-2 px-4">Datetime</th>
                <th className="py-2 px-4">Name</th>
                <th className="py-2 px-4">Location</th>
                <th className="py-2 px-4">ZIP</th>
                <th className="py-2 px-4">Amount</th>
                <th className="py-2 px-4">Balance</th>
                <th className="py-2 px-4">Fraud?</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction, index) => (
                <tr key={index} className="text-black border-t border-black">
                  <td>{transaction.DateTime}</td>
                  <td>{transaction.Name}</td>
                  <td>{transaction.Location}</td>
                  <td>{transaction.Zip}</td>
                  <td>{transaction.Amount}</td>
                  <td>{transaction.Balance}</td>
                  <td>{transaction.Fraud ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}

export default App;
