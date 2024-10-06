#!/bin/bash

# Function to check if a port is in use
check_and_kill_port() {
  local port=$1
  local service_name=$2

  # Check if the port is in use
  if lsof -i :$port &> /dev/null; then
    echo "$service_name is already running on port $port. Terminating the process."
    # Find the PID of the process using the port and kill it
    pid=$(lsof -t -i :$port)
    kill -9 $pid
    echo "$service_name process (PID: $pid) killed."
  else
    echo "$service_name port $port is free."
  fi
}

# Check Zookeeper port (2181)
check_and_kill_port 2181 "Zookeeper"

# Check Kafka port (9092)
check_and_kill_port 9092 "Kafka"

# Set the path to your Kafka installation
KAFKA_DIR="kafka_2.13-3.8.0"  # Replace this with your Kafka installation path

# Function to start Zookeeper
start_zookeeper() {
    echo "Starting Zookeeper..."
    nohup "$KAFKA_DIR/bin/zookeeper-server-start.sh" "$KAFKA_DIR/config/zookeeper.properties" > logs/zookeeper.log 2>&1 &
    sleep 5  # Wait for Zookeeper to start
    echo "Zookeeper started."
}

# Function to start Kafka broker
start_kafka() {
    echo "Starting Kafka broker..."
    nohup "$KAFKA_DIR/bin/kafka-server-start.sh" "$KAFKA_DIR/config/server.properties" > logs/kafka.log 2>&1 &
    sleep 5  # Wait for Kafka to start
    echo "Kafka broker started."
}

# Main script execution
start_zookeeper
start_kafka

echo "Kafka and Zookeeper are running."
echo "Check 'zookeeper.log' and 'kafka.log' for output."
echo "Press Ctrl+C to stop."

# Keep the script running
while true; do
    sleep 1
done
