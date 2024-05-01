from pymongo import MongoClient
from flask import Flask, Response
from bson import ObjectId
import json
import os

username = os.getenv('MONGO_USERNAME')  # Set this in your environment
password = os.getenv('MONGO_PASSWORD')  # Set this in your environment
dbname = "clinics"
cluster_url = "cluster0.jmmyofl.mongodb.net"

# Corrected MongoClient initialization
client = MongoClient(f"mongodb+srv://{username}:{password}@{cluster_url}/{dbname}?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
db = client[dbname]

def mongo_jsonify(data):
    class MongoEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    return Response(
        json.dumps(data, cls=MongoEncoder),
        mimetype='application/json'
    )

def mongo_jsonify_list(data_list):
    class MongoEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    formatted_data = [MongoEncoder().encode(item) for item in data_list]
    return Response(
        f'[{", ".join(formatted_data)}]',
        mimetype='application/json'
    )
