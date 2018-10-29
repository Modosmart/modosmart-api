#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, Response
import ble_manage
import symbiote_manage
import re
import requests
import json
import socket

PUBLIC_RESOURCES = 'https://symbioteweb.eu.ngrok.io/innkeeper/public_resources'
AC_SWITCH_IP_ADDRESS = '192.168.1.102'
AC_SWITCH_PORT = 3310
AC_SWITCH_MAC_ADDRESS = 'fa:16:3e:c0:ba:42'
AC_SWITCH_NAME = 'AcSwitch'
BUFFER_SIZE = 1024

app = Flask(__name__)

# @app.route('/', defaults={'path': ''}, methods=['POST'])
# @app.route('/<path:path>', methods=['POST'])
# def catch_all(path):
#     print 'Catch all'
#     print 'You want path: %s' % path
#     print request.get_data()
#     return 'You want path: %s' % path

@app.route('/')
def index():
    return "Hello, World!"


@app.route('/api/scan', methods=['GET'])
def scan_devices():
    devices = scan_register()
    return jsonify(devices)

@app.route('/api/register_switch', methods=['POST'])
def register_switch():
    symbiote_manage.register_ac_switch(AC_SWITCH_MAC_ADDRESS, AC_SWITCH_NAME)
    return jsonify('OK')

@app.route('/api/unregister/room_sensor/<ssp_id>', methods=['POST'])
def unregister_room_sensor(ssp_id):
    addr = request.form['mac_address']
    innk_resp = symbiote_manage.unregister_room_sensor(addr, ssp_id)
    return Response(innk_resp.text, status=innk_resp.status_code)


@app.route('/api/<sensor_id>/Observations', methods=['POST'])
def read_resource(sensor_id):
    id = re.findall(r"\'(.*?)\'", sensor_id)
    symIdResource = id[0]
    response = requests.get(PUBLIC_RESOURCES)

    resources = json.loads(response.text)
    mac_address = ''
    for resource in resources:
        resource_obj = resource['resource']
        resource_id = resource_obj['id']
        resource_name = resource_obj['name']
        # if "SM006_" not in resource_name:
        #     continue
        if resource_id == symIdResource:
            # this is the resource required to get readings for
            if "SM006_" in resource_name:
                # get mac address
                mac_address = resource_name.replace('SM006_', '')
                break
    # Connect to the required mac address and get readings
    final_response = {}
    print mac_address
    if (mac_address != ''):
        final_response = ble_manage.read_room_sensor(mac_address)

    return jsonify(final_response)


@app.route('/rap/room_sensor', methods=['POST'])
def read_resource_rap():
    print 'Reading room sensor'
    request_data = json.loads(request.get_data())
    resourceInfo = request_data['resourceInfo']
    symIdResource = resourceInfo[0]['symIdResource']

    response = requests.get(PUBLIC_RESOURCES)

    resources = json.loads(response.text)
    mac_address = ''
    for resource in resources:
        resource_obj = resource['resource']
        resource_id = resource_obj['id']
        resource_name = resource_obj['name']
        # if "SM006_" not in resource_name:
        #     continue
        if resource_id == symIdResource:
            # this is the resource required to get readings for
            if "SM006_" in resource_name:
                # get mac address
                mac_address = resource_name.replace('SM006_', '')
                break
    # Connect to the required mac address and get readings
    final_readings = {}
    print mac_address
    if (mac_address != ''):
        final_readings = ble_manage.read_room_sensor(mac_address)

    # temperature = final_readings['temperature']
    # humidity = final_readings['humidity']
    # battery = final_readings['battery']
    # presence = final_readings['presence']
    # fw_version = final_readings['firmware']

    # print str(presence)
    # final_response = str('{\
    #         "resourceId": "' + mac_address + '",\
    #         "location": {\
    #             "longitude": -2.944728,\
    #             "latitude": 43.26701,\
    #             "altitude": 20\
    #         },\
    #         "resultTime": "1970-1-1T02:00:12",\
    #         "samplingTime": "1970-1-1T02:00:12",\
    #         "obsValues": [\
    #             {\
    #                 "value": "' + str(temperature) + '",\
    #                 "obsProperty": {\
    #                     "@c": ".Property",\
    #                     "name": "temperature",\
    #                     "description": ""\
    #                 },\
    #                 "uom": {\
    #                     "@c": "UnitOfMeasurment",\
    #                     "symbol": "C",\
    #                     "name": "C",\
    #                     "description": ""\
    #                 }\
    #             },\
    #             {\
    #                 "value": "' + str(humidity) + '",\
    #                 "obsProperty": {\
    #                     "@c": ".Property",\
    #                     "name": "humidity",\
    #                     "description": ""\
    #                 },\
    #                 "uom": {\
    #                     "@c": "UnitOfMeasurment",\
    #                     "symbol": "%",\
    #                     "name": "%",\
    #                     "description": ""\
    #                 }\
    #             },\
    #             {\
    #                 "value": "' + str(battery) + '",\
    #                 "obsProperty": {\
    #                     "@c": ".Property",\
    #                     "name": "batteryLevel",\
    #                     "description": ""\
    #                 },\
    #                 "uom": {\
    #                     "@c": "UnitOfMeasurment",\
    #                     "symbol": "%",\
    #                     "name": "%",\
    #                     "description": ""\
    #                 }\
    #             },\
    #             {\
    #                 "value": "' + str(presence) + '",\
    #                 "obsProperty": {\
    #                     "@c": ".Property",\
    #                     "name": "activity",\
    #                     "description": ""\
    #                 },\
    #                 "uom": {\
    #                     "@c": "UnitOfMeasurment",\
    #                     "symbol": "",\
    #                     "name": "",\
    #                     "description": ""\
    #                 }\
    #             }\
    #         ]\
    #     }').decode("utf8")
    return jsonify(final_readings)

def scan_register():
    devices = ble_manage.scan_room_sensor()
    for dev in devices:
        # Register devices
        symbiote_manage.register_room_sensor(dev['mac_address'], dev['name'])
    return devices

def control_switch(status):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((AC_SWITCH_IP_ADDRESS, AC_SWITCH_PORT))
    if (status == 0):
        s.send('SET,1:ONOFF,OFF\r')
    else:
        s.send('SET,1:ONOFF,ON\r')
    data = s.recv(BUFFER_SIZE)
    s.close()
    return data

if __name__ == '__main__':
    # control_switch(1)
    # scan_register()
    app.run(debug=True, host='0.0.0.0', port=3030)
