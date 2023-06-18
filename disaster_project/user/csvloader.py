import pandas as pd
from django.conf import settings
from pymongo import MongoClient
import uuid

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'djongo',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'localhost',
            'port': 27017,
            'username': 'root',
            'password': 'example',
        }
    }
}
csv_file_path = '/Users/meltemkoc/Desktop/HOSPITALS.csv'
df = pd.read_csv(csv_file_path)
database_settings = DATABASES['default']
host = database_settings['CLIENT']['host']
port = database_settings['CLIENT']['port']
username = database_settings['CLIENT']['username']
password = database_settings['CLIENT']['password']
client = MongoClient(host, port, username=username, password=password)
database_name = database_settings['NAME']
collection_name = 'user_hospitals'
db = client[database_name]
collection = db[collection_name]
import uuid


for _, row in df.iterrows():
    hospital_data = {
        'id': str(uuid.uuid4()),  # Generate a unique ID
        'name': row['place'],
        'city': row['city'],
        'lat': row['Latitude'],
        'lon': row['Longitude']
    }
    
    existing_document = collection.find_one({'id': hospital_data['id']})
    if existing_document:
        print(f"Skipping duplicate document with id: {hospital_data['id']}")
    else:
        collection.insert_one(hospital_data)