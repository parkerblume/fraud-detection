from confluent_kafka import Producer
import pandas as pd
import time

data_dir = 'myenv/data/'

# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092'  # Replace with your Kafka broker URL if not local
}

def kafka_producer(file):
    producer = Producer(kafka_config)
    
    # Read the CSV file
    transactions_df = pd.read_csv(file, delimiter='\t')
    
    # Optional: Check if CSV loaded properly
    print("CSV Loaded: \n", transactions_df.head())
    
    def delivery_report(err, msg):
        if err:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    # Send each row of the CSV to Kafka
    for _, transaction in transactions_df.iterrows():
        message = transaction.to_json().encode('utf-8')  # Convert row to JSON string and encode to bytes
        producer.produce('transactions', value=message, callback=delivery_report)
        producer.poll(0)  # Ensure messages are sent immediately
        time.sleep(0.1)  # Optional: Simulate delay between messages

    # Wait for any remaining messages to be delivered
    producer.flush()

if __name__ == "__main__":
    kafka_producer(data_dir + 'camilo.txt')
