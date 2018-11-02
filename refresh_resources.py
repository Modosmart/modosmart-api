import requests
import time

while True:
    time.sleep(1800) # wait for 30 minutes
    response = requests.get('http://localhost:3030/api/scan')
    print response
