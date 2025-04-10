from flask import Flask, request, jsonify
from pymongo import MongoClient
import joblib
from datetime import datetime, timedelta

import requests

DISCORD_WEBHOOK_URL = "🔗 PASTE YOUR WEBHOOK URL HERE"

def send_discord_alert(ip, username):
    message = {
        "content": f"🚨 **INTRUSION DETECTED** 🚨\n"
                   f"IP: `{ip}`\nUsername: `{username}`\nTime: `{datetime.utcnow()}`"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=message)
    except Exception as e:
        print("Failed to send Discord alert:", e)

app = Flask(__name__)

# Load your trained model
model = joblib.load("ids_model.pkl")

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017")  # 🔁 Replace with Atlas URI if needed
db = client["ids_system"]
collection = db["login_attempts"]

# In-memory blocklist
blocked_ips = {}

@app.route("/login", methods=["POST"])
def login():
    ip = request.remote_addr
    now = datetime.now()

    # Blocked IP check
    if ip in blocked_ips and blocked_ips[ip] > now:
        return jsonify({"status": "blocked", "message": "Access denied"}), 403

    username = request.form.get("user")
    password = request.form.get("pass")

    # Feature extraction based on past attempts
    past_attempts = list(collection.find({
        "ip": ip,
        "timestamp": {"$gte": datetime.utcnow() - timedelta(minutes=1)}
    }))
    features = [len(password), len(past_attempts)]

    # Prediction
    pred = model.predict([features])[0]

    # Store in DB
    attempt_data = {
        "ip": ip,
        "timestamp": datetime.utcnow(),
        "username": username,
        "password_len": len(password),
        "intrusion": bool(pred),
        "result": "success" if password == "admin123" else "fail"
    }
    collection.insert_one(attempt_data)

    # Block if needed
    if pred == 1:
        blocked_ips[ip] = now + timedelta(minutes=15)
        return jsonify({"status": "blocked", "message": "Intrusion detected. IP blocked!"}), 403

    if password == "admin123":
        return jsonify({"status": "success", "message": "Login successful!"})
    else:
        return jsonify({"status": "fail", "message": "Invalid credentials."}), 401

if __name__ == "__main__":
    app.run(debug=True)
