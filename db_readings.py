import json
from pymongo import MongoClient

def read_db(records):
    readings = []
    client = MongoClient('localhost', 27017)
    db = client['modosmart']
    collection = db['sensors_readings']
    for doc in collection.find().sort([('_id', 1)]).limit(records):
        readings.append(doc)
    return readings
