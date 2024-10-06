import React, { useEffect, useState } from "react";
import io from "socket.io-client";

const socket = io("http://localhost:5000"); // Connect to Flask WebSocket server

const TransactionFeed = () => {
	const [transactions, setTransactions] = useState([]);

	useEffect(() => {
		socket.on("connect", () => {
			console.log("Connected to WebSocket");
		});

		const handleNewTransaction = (data) => {
			console.log("Received transaction:", data);
			setTransactions((prev) => [...prev, data.transaction]);
		};

		socket.on("new_transaction", handleNewTransaction);

		return () => {
			socket.off("new_transaction");
			//socket.disconnect();
		};
	}, []);

	return (
		<table>
			<thead>
				<tr>
					<th className="py-2 px-4">Date</th>
					<th className="py-2 px-4">Time</th>
					<th className="py-2 px-4">Name</th>
					<th className="py-2 px-4">Location</th>
					<th className="py-2 px-4">ZIP</th>
					<th className="py-2 px-4">Amount</th>
					<th className="py-2 px-4">Balance</th>
				</tr>
			</thead>
			<tbody>
				{transactions.map((transaction, index) => (
					<tr key={index} className="text-black border-t border-black">
						<td className="py-2 px-4">{transaction.Date}</td>
						<td className="py-2 px-4">{transaction.Time}</td>
						<td className="py-2 px-4">{transaction.Name}</td>
						<td className="py-2 px-4">{transaction.Location}</td>
						<td className="py-2 px-4">{transaction.Zip}</td>
						<td className="py-2 px-4">{transaction.Amount}</td>
						<td className="py-2 px-4">{transaction.Balance}</td>
						<td className="py-2 px-4"></td>
					</tr>
				))}
			</tbody>
		</table>
	);
};

export default TransactionFeed;
