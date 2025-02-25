import os
import requests
from flask import Flask, abort, jsonify, request
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_SRV_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_COLLECTION = os.getenv("DATABASE_COLLECTION")

client = MongoClient(MONGO_URI)
db = client.get_database(DATABASE_NAME)
humidity_collection = db.get_collection(DATABASE_COLLECTION)

# Ubidots Configuration
UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
UBIDOTS_DEVICE = "esp32"
UBIDOTS_VARIABLES = ["humidity", "temperature"]


def send_to_ubidots(data):
    """Send data to Ubidots"""
    url = f"https://industrial.api.ubidots.com/api/v2.0/devices/{UBIDOTS_DEVICE}/"
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201]:
        return {
            "message": "Data sent to Ubidots successfully",
            "response": response.json(),
        }
    else:
        return {
            "error": "Failed to send data to Ubidots",
            "status_code": response.status_code,
            "response": response.text,
        }


@app.route("/data/<token>", methods=["GET"])
def show_humidity(token):
    if token != os.getenv("SECRET_KEY"):
        abort(401)

    latest_data = humidity_collection.find_one({}, sort=[("_id", -1)])

    if not latest_data:
        return jsonify({"message": "No data available"}), 404

    return jsonify(
        {
            "humidity": latest_data.get("humidity", "N/A"),
            "temperature": latest_data.get("temperature", "N/A"),
            "timestamp": latest_data.get("timestamp", "N/A"),
        }
    )


@app.route("/data/<token>", methods=["POST"])
def post_humidity(token):
    if token != os.getenv("SECRET_KEY"):
        abort(401)

    data = request.json
    if not data or not all(field in data for field in UBIDOTS_VARIABLES):
        return jsonify({"error": "Missing required data (humidity, temperature)"}), 400

    new_record = {
        "humidity": data["humidity"],
        "temperature": data["temperature"],
        "timestamp": datetime.utcnow(),
    }

    # Store in MongoDB
    humidity_collection.insert_one(new_record)

    # Send to Ubidots
    ubidots_response = send_to_ubidots(
        {"humidity": data["humidity"], "temperature": data["temperature"]}
    )

    return (
        jsonify(
            {
                "message": "Data saved successfully",
                "data": new_record,
                "ubidots": ubidots_response,
            }
        ),
        201,
    )


@app.route("/health", methods=["GET"])
def health_check():
    return "Fortunately, I'm Alive!"


if __name__ == "__main__":
    app.run(debug=True, port=3232)
