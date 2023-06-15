import pandas as pd
from pymongo import MongoClient
from django.conf import settings

csv_file_path = 'C:\\Users\\m-omo\\OneDrive\\Desktop\\HOSPITALS.csv'

client = MongoClient('mongodb://localhost:27017')
db = client['djongo']
collection = db['user_hospitals']

df = pd.read_csv(csv_file_path)
for _, row in df.iterrows():
    hospital_data = {
        'name': row['place'],
        'city': row['city'],
        'lat': row['Latitude'],
        'lon': row['Longitude']
    }
    collection.insert_one(hospital_data)




