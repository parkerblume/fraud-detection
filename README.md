# Knights BNY Fraud Detection Challenge

This project was created during the KnightHacks 7 Hackathon. BNY Mellon was a sponsor of this year's event and provided the hackathon a problem that we found very interesting and wanted to provide a creative solution, and this solution is explained below.

## The Problem

Financial fraud (e.g. identity theft, transaction fraud) is a persistent challenge. Develop an AI model that analyzes real-time transactions to detect suspicious activity. Use historical transaction data and patterns to build a machine learning model that flags anomalies.

## Our Solution

We implemented a Random Forest Classification Model to best find outlier's in a person's patterns of transactions.

### Synthetic Date Generation

Since bank statements are a hard dataset to come upon due to the sensitivity around it, we created a synthetic generation script to create the data used to the train our model. This data creates a typical pattern of a person's transactions (this pattern will be touched more on in the model section).

### The Model

The model we've decided is a Random Forest Classification Model, this seems to be best when trying to find outliers (or anomalies) in a data set and is better able to predict possible fraudulent purchases.

Using the synthetic data, we trained the model to find the person's spending pattern with numerous feature inputs:
* The city they frequently purchase items from
* Their typical times of purchases
* The amount of the purchase
* Credit and Age (adds to the bias)

We've also engineered a few features to give more importance on the pattern of these purchases:
* The days of the week, to allow for flexibility where maybe the person spends more on saturdays then they do on tuesdays.
* Unusual times for purchases
* The amount spent within some hour given by Z-score.

### The Frontend

The frontend we kept simple as within our 2 hour time span of the competition we had to. The frontend is able to upload a bank statement in the form of a .csv which is then sent to the backend python server to train the model on the user's pattern of purchases.

We then implement a simulation for real-time transactions, where the model provides a probability for each real-time transaction. When the frontend recieves the probability we then classify the transaction using the probability as either "Low Risk" (40-60%), "Medium Risk" (60%-80%), or "High Risk" (>80%).

## Prerequisites

* python 3.0 or greater

## To set up

1. Clone the repository
2. Create the venv: `python -m venv myenv`
3. Activate the environment by navigating the project folder then run:
    * On Windows:
    `myenv\Scripts\Activate`
    * On Linux:
    `source myenv/bin/activate`
4. Install the packages: `pip install -r requirements.txt`
5. To deactivate the environment simply type `deactivate`

## Adding new packages
Simply run `pip install package` and update the requirements with `pip freeze > requirements.txt`

## To run server
With the environment activated, run `uvicorn main:app --reload`