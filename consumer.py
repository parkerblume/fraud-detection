from confluent_kafka import Consumer

# Kafka consumer configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'test-consumer-group',
    'auto.offset.reset': 'earliest'  # Start reading from the beginning of the topic
}

def kafka_consumer():
    consumer = Consumer(kafka_config)
    
    # Subscribe to the 'transactions' topic
    consumer.subscribe(['transactions'])
    
    try:
        while True:
            msg = consumer.poll(1.0)  # Poll for new messages (timeout = 1 second)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Decode the message and print
            print(f"Received message: {msg.value().decode('utf-8')}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    kafka_consumer()
