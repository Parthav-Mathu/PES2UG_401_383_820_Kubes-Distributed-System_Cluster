from flask import Flask, request, jsonify, render_template, redirect
from pymongo import MongoClient
from datetime import datetime
import uuid

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["CC_PROJECT"]
nodes_collection = db["A Distributed Systems Cluster Simulation Framework"]

# Register a Node (POST)
@app.route("/register", methods=["POST"])
def register_node():
    node_id = request.form.get("node_id")
    cpu_cores = request.form.get("cpu_cores")

    if not node_id or not cpu_cores:
        return "Missing Node ID or CPU Cores!", 400

    cpu_cores = int(cpu_cores)

    # Check if node already exists
    if nodes_collection.find_one({"node_id": node_id}):
        return "Node ID already exists!", 400

    # Save to MongoDB
    nodes_collection.insert_one({
        "node_id": node_id,
        "cpu_cores": cpu_cores,
        "available_cores": cpu_cores,
        "status": "healthy",
        "pods": [],
        "last_heartbeat": datetime.utcnow()
    })
    return redirect("/")

# Launch a Pod with Best/Worst Fit Scheduling
@app.route("/launch_pod", methods=["POST"])
def launch_pod():
    cpu_required = int(request.form.get("cpu_cores"))
    policy = request.form.get("scheduling_policy")  # "best_fit" or "worst_fit"

    nodes = list(nodes_collection.find({"status": "healthy", "available_cores": {"$gte": cpu_required}}))

    if not nodes:
        return "No suitable nodes found!", 400

    if policy == "best_fit":
        selected_node = min(nodes, key=lambda x: x['available_cores'])
    elif policy == "worst_fit":
        selected_node = max(nodes, key=lambda x: x['available_cores'])
    else:
        return "Invalid scheduling policy!", 400

    pod_id = f"pod_{uuid.uuid4().hex[:6]}"
    new_pod = {
        "pod_id": pod_id,
        "cpu_cores": cpu_required,
        "status": "running",
        "created_at": datetime.utcnow()
    }

    # Update node with new pod
    nodes_collection.update_one(
        {"node_id": selected_node["node_id"]},
        {
            "$push": {"pods": new_pod},
            "$inc": {"available_cores": -cpu_required}
        }
    )

    return jsonify({
        "message": "Pod successfully launched!",
        "pod_id": pod_id,
        "assigned_node": selected_node["node_id"]
    })

# List Nodes (GET)
@app.route("/nodes", methods=["GET"])
def list_nodes():
    nodes = list(nodes_collection.find({}, {"_id": 0}))
    return jsonify(nodes)

# Web Interface for Node Registration and Pod Launch
@app.route("/", methods=["GET"])
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
<title>Cluster Simulation</title>
</head>
<body>
<h2>Register a New Node</h2>
<form action="/register" method="post">
<label for="node_id">Node ID:</label>
<input type="text" name="node_id" required><br>
<label for="cpu_cores">CPU Cores:</label>
<input type="number" name="cpu_cores" required><br>
<button type="submit">Register</button>
</form>

<h2>Launch a Pod</h2>
<form action="/launch_pod" method="post">
<label for="cpu_cores">CPU Cores Required:</label>
<input type="number" name="cpu_cores" required><br>
<label for="scheduling_policy">Scheduling Policy:</label>
<select name="scheduling_policy">
  <option value="best_fit">Best Fit</option>
  <option value="worst_fit">Worst Fit</option>
</select><br>
<button type="submit">Launch Pod</button>
</form>

<h3>View Registered Nodes: <a href="/nodes">Click Here</a></h3>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True, port=5000)
