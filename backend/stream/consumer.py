from confluent_kafka import Consumer
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS
import threading
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")  # Set this for SocketIO too

# Kafka Consumer Configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'fraud_detection_group',
    'auto.offset.reset': 'earliest'
}

def consume_transactions():
    consumer = Consumer(consumer_config)
    consumer.subscribe(['transactions'])  # Subscribe to the 'transactions' topic

    try:
        while True:
            msg = consumer.poll(1.0)  # Wait for a message for 1 second

            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Decode the message and emit it to WebSocket clients
            transaction = json.loads(msg.value().decode('utf-8'))
            print(f"Consumed transaction: {transaction}")
            print("Emitting transaction...")  # Log before emitting
            socketio.emit('new_transaction', {'transaction': transaction})
            print("Transaction emitted.")  # Log after emitting
    finally:
        consumer.close()

# WebSocket connection handler
@socketio.on('connect')
def handle_connect():
    print("Client connected")

if __name__ == '__main__':
    kafka_thread = threading.Thread(target=consume_transactions)
    kafka_thread.start()

    # Run the Flask WebSocket server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
