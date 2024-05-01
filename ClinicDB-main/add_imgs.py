import os
import random

def list_image_files(folder_path):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png'))]

image_files = list_image_files('C:/Users/13236/Documents/GitHub/Grocery/sql/images/')

def convert_image_to_binary(image_path):
    with open(image_path, 'rb') as file:
        return file.read()

from pymongo import MongoClient
username = os.getenv('MONGO_USERNAME')  # Set this in your environment
password = os.getenv('MONGO_PASSWORD')  # Set this in your environment
# MongoDB setup
dbname = "clinics"
cluster_url = "cluster0.jmmyofl.mongodb.net"
client = MongoClient(f"mongodb+srv://{username}:{password}@{cluster_url}/{dbname}?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
db = client['clinics']
visit_form_collection = db['visit_form']

for document in visit_form_collection.find():
    random_image_path = random.choice(image_files)
    binary_data = convert_image_to_binary(random_image_path)

    visit_form_collection.update_one(
        {'_id': document['_id']},
        {'$set': {'VisitFormImg': binary_data}}
    )

