import requests
import time
import json

while True:
    time.sleep(1800) # wait for 30 minutes
    # response = requests.get('http://localhost:3030/api/scan')
    # get public resources
    public_resources = requests.get(
        'https://symbioteweb.eu.ngrok.io/innkeeper/public_resources')
    resources = json.loads(public_resources.text)
    for resource in resources:
        resource_obj = resource['resource']
        # resource_id = resource_obj['id']
        resource_name = resource_obj['name']
        resource_type = resource_obj['@c']
        mac_address = ''
        ssp_id = ''
        if (resource_type == '.StationarySensor'):
            mac_address = resource_name.replace('SM006_', '')
            strings_slices = mac_address.split("_")
            mac_address = strings_slices[0]
            ssp_id = strings_slices[1]
        elif (resource_type == '.Actuator'):
            mac_address = resource_name.replace('AC_SWITCH_', '')
            strings_slices = mac_address.split("_")
            mac_address = strings_slices[0]
            ssp_id = strings_slices[1]
        print(mac_address)
        print(ssp_id)
        if (mac_address != ''):
            body = {}
            # body['mac_address'] = mac_address
            body['ssp_id'] = ssp_id
            json_data = json.dumps(body)
            response = requests.post(
                'http://localhost:3030/api/keep_alive', json=json_data)
    print response
