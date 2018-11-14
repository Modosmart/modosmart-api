import symbiote_manage
import time
import json
from pymongo import MongoClient
import requests

client = MongoClient('localhost', 27017)
db = client['modosmart']
collection = db['sensors_readings']

while True:
    # get public resources
    public_resources = requests.get(
        'https://symbioteweb.eu.ngrok.io/innkeeper/public_resources')
    if public_resources.status_code != 200:
        time.sleep(120)  # wait for 2 minutes
        # Don't! If you catch, likely to hide bugs.
        raise Exception('Service not still running')
        continue
    resources = json.loads(public_resources.text)
    for resource in resources:
        resource_obj = resource['resource']
        resource_id = resource_obj['id']
        resource_name = resource_obj['name']
        resource_type = resource_obj['@c']
        if (resource_type == '.StationarySensor'):
            json_response = symbiote_manage.get_reading_room_sensor(
                resource_id)
            reading_id = collection.insert_one(json_response).inserted_id
    time.sleep(300)  # wait for 5 minutes
