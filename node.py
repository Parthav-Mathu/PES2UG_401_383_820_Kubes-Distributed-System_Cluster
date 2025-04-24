import time
import requests
import socket

API_SERVER_URL = "http://localhost:5000"
NODE_NAME = socket.gethostname()
CPU_CORES = 2  # Modify as needed

# Register the node with the API server
def register_node():
    response = requests.post(f"{API_SERVER_URL}/register", data={
        "node_id": NODE_NAME,
        "cpu_cores": CPU_CORES
    })
    if response.status_code == 200:
        print(f"Node {NODE_NAME} registered successfully.")
    else:
        print(f"Failed to register node: {response.text}")

# Send heartbeat signals to the API server
def send_heartbeat():
    while True:
        try:
            requests.post(f"{API_SERVER_URL}/heartbeat", json={"node_name": NODE_NAME})
            print(f"Heartbeat sent from {NODE_NAME}.")
        except Exception as e:
            print(f"Failed to send heartbeat: {e}")
        time.sleep(5)  # Send heartbeat every 5 seconds

# Trigger pod launch
def launch_pod(cpu_cores, method="best_fit"):
    response = requests.post(f"{API_SERVER_URL}/launch_pod", json={
        "cpu_cores": cpu_cores,
        "method": method
    })
    if response.status_code == 200:
        print(f"Pod launched successfully: {response.json()}")
    else:
        print(f"Failed to launch pod: {response.text}")

if __name__ == "__main__":
    register_node()
    send_heartbeat()
    # Example of launching a pod with 2 CPU cores using best_fit method
    launch_pod(2, "best_fit")
