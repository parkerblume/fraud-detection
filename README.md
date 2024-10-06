# Knights BNY Fraud Detection Challenge

## Prerequisites

-   python 3.0 or greater

## To set up

1. Clone the repository
2. Create the venv: `python -m venv myenv`
3. Activate the environment by navigating the project folder then run:
    - On Windows:
      `myenv\Scripts\Activate`
    - On Linux:
      `source myenv/bin/activate`
4. Install the packages: `pip install -r requirements.txt`
5. To deactivate the environment simply type `deactivate`

## Adding new packages

Simply run `pip install package` and update the requirements with `pip freeze > requirements.txt`

## Running Kafka and Flask

1. `cd backend/stream`
2. Run `./start_backend.sh` to start Zookeeper and the Kafka broker
3. Open a new terminal window and run `python consumer.py` to start the Flask websocket server
4. Open a new terminal window and `cd client`
5. `npm install` to install frontend dependencies
6. Open a new terminal window and `cd backend/stream`
7. Run `python producer.py` to parse the CSV and begin sending transactions to Kafka
