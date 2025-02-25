import os
from flask import Flask, abort, jsonify, request
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_SRV_URI")
client = MongoClient(MONGO_URI)
db = client.get_database(os.getenv("DATABASE_NAME"))
humidity_collection = db.get_collection(os.getenv("DATABASE_COLLECTION"))

data_struct = [
    "humidity",
    "temperature",
]


@app.route('/data/<token>', methods=['GET'])
def show_humidity(token):
    if token != os.getenv('SECRET_KEY'):
        abort(401)

    humidity_data = humidity_collection.find_one({}, sort=[("_id", -1)])

    if not humidity_data:
        return jsonify({"message": "No humidity data available"}), 404

    return jsonify(
        {"humidity": humidity_data.get("humidity", "N/A"), "timestamp": humidity_data.get("timestamp", "N/A")})


@app.route('/data/<token>', methods=['POST'])
def post_humidity(token):
    if token != os.getenv('SECRET_KEY'):
        abort(401)

    data = request.json
    if not data or data_struct not in data:
        return jsonify({"error": "Missing humidity data"}), 400

    # Insert new humidity record into MongoDB
    new_record = {
        "humidity": data["humidity"],
        "temperature": data["temperature"],
        "timestamp": datetime
    }
    humidity_collection.insert_one(new_record)

    return jsonify({"message": "Humidity data saved successfully", "data": new_record}), 201


@app.route("/health", methods=['GET'])
def hello():
    return "Fortunately, I'm Alive!"


if __name__ == '__main__':
    app.run(debug=True)
