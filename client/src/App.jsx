import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import TransactionFeed from "/components/TransactionFeed";

function App() {
	return (
		<>
			<div className="flex flex-col w-full h-full p-3">
				<h1>Real-time Fraud Detection System</h1>
				<div className="flex flex-col text-black bg-white justify-center rounded-xl items-stretch p-3">
					<TransactionFeed />
				</div>
			</div>
		</>
	);
}

export default App;
