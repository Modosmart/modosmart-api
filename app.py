#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, Response
import ble_manage
import symbiote_manage
import re
import requests
import json
from socket import *
import db_readings
# import time

PUBLIC_RESOURCES = 'https://symbioteweb.eu.ngrok.io/innkeeper/public_resources'
AC_SWITCH_PORT = 3310
BUFFER_SIZE = 1024

app = Flask(__name__)


# @app.route('/', defaults={'path': ''}, methods=['POST'])
# @app.route('/<path:path>', methods=['POST'])
# def catch_all(path):
#     print 'Catch all'
#     print 'You want path: %s' % path
#     print request.get_data()
#     return jsonify('reponse ok')


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/api/scan', methods=['GET'])
def scan_devices():
    devices = scan_register()
    return jsonify(devices)


# @app.route('/api/register_switch', methods=['POST'])
# def register_switch():
#     response = symbiote_manage.register_ac_switch(
#         '00:1D:C9:A1:89:00', '192.168.1.23', "AC_SWITCH")
#     return jsonify('OK')


@app.route('/api/unregister', methods=['POST'])
def unregister_resource():
    ssp_id = request.form['ssp_id']
    innk_resp = symbiote_manage.unregister_room_sensor(ssp_id)
    return Response(innk_resp.text, status=innk_resp.status_code)


@app.route('/api/keep_alive', methods=['POST'])
def resource_keep_alive():
    print('Keep alive called')
    # ssp_id = request.form['ssp_id']
    req_data = json.loads(request.get_json())
    ssp_id = req_data['ssp_id']
    print(ssp_id)
    innk_resp = symbiote_manage.send_keep_alive(ssp_id)
    print(innk_resp.status_code)
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
                strings_slices = mac_address.split("_")
                mac_address = strings_slices[0]
                break
    # Connect to the required mac address and get readings
    final_response = {}
    print mac_address
    if (mac_address != ''):
        final_response = ble_manage.read_room_sensor(mac_address)

    return jsonify(final_response)


@app.route('/rap/ac_switch', methods=['GET', 'POST', 'PUT', 'DELETE'])
def ac_resource_rap():
    print 'Control AC Switch'
    # GET IP Address
    request_data = json.loads(request.get_data())
    resourceInfo = request_data['resourceInfo']
    ip_address = resourceInfo[0]['internalIdResource']
    parameters_array = request_data['body']['OnOffCapabililty']
    if len(parameters_array) < 2:
        return Response('number of parameters is not correct', status=404)
    on_parameter_found = False
    control_parameter_found = False
    control = 0
    on = 0
    for i in range(len(parameters_array)):
        current_parameter = parameters_array[i]
        if 'on' in current_parameter:
            on_parameter_found = True
            on = current_parameter['on']
        if 'control' in current_parameter:
            control_parameter_found = True
            control = current_parameter['control']

    if (not on_parameter_found or not control_parameter_found):
        return Response('couldnot find on or control', status=404)

    if (control == 1):
        print 'Need Control'
        control_switch(on, ip_address)
    current_status_string = get_control_switch(ip_address)
    current_status = {}
    current_status['status'] = current_status_string
    json_data = json.dumps(current_status)

    return jsonify(current_status)


@app.route('/rap/room_sensor', methods=['POST'])
def read_resource_rap():
    print 'Reading room sensor'
    request_data = json.loads(request.get_data())
    resourceInfo = request_data['resourceInfo']
    symIdResource = resourceInfo[0]['symIdResource']
    print(request_data)

    type = request_data['type']

    if (type == 'GET'):
        json_response = symbiote_manage.get_reading_room_sensor(symIdResource)
        final_response_array = []
        final_response_array.append(json_response)
        return jsonify(final_response_array)
    elif (type == 'HISTORY'):
        # read records from db
        records_required = request_data['top']
        readings = db_readings.read_db(records_required)
        return jsonify(readings)

def scan_register():
    devices = []
    ble_devices = ble_manage.scan_room_sensor()
    devices.append(ble_devices)
    for dev in ble_devices:
        # Register devices
        symbiote_manage.register_room_sensor(dev['mac_address'], dev['name'])
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto('DISCOVER\r', ('255.255.255.255', 3310))
        # time.sleep(5)

        s1 = socket(AF_INET, SOCK_DGRAM)
        s1.bind(('', 3310))
        s1.settimeout(5.0)  # 5 seconds
        m = s1.recvfrom(1024)
        wifi_devices_string = m[0]
        mylist = wifi_devices_string.split(',')

        ac_switch_mac_address = mylist[1]
        final_ac_switch_mac_address = ac_switch_mac_address[:2] + ':' + ac_switch_mac_address[2:4] + ':' + ac_switch_mac_address[4:6] + \
            ':' + ac_switch_mac_address[6:8] + ':' + \
            ac_switch_mac_address[8:10] + ':' + ac_switch_mac_address[10:12]

        current_device = {}
        current_device['mac_address'] = final_ac_switch_mac_address
        current_device['name'] = 'AC_SWITCH'
        current_device['type'] = 'ac_switch'
        current_device['ip_address'] = mylist[2]

        json_data = json.dumps(current_device)

        devices.append(current_device)

        s.close()
        s1.close()

        symbiote_manage.register_ac_switch(
            current_device['mac_address'], current_device['ip_address'], current_device['name'])
    except:
        print 'Error reading ac switch'

    print devices
    return devices


def control_switch(status, ip_address):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((ip_address, AC_SWITCH_PORT))
    if (status == 0):
        s.send('SET,1:ONOFF,OFF\r')
    else:
        s.send('SET,1:ONOFF,ON\r')
    s.settimeout(5.0)  # 5 seconds
    data = s.recv(BUFFER_SIZE)
    print data
    s.settimeout(None)
    s.close()
    return data


def get_control_switch(ip_address):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((ip_address, AC_SWITCH_PORT))
    s.send('GET,1:ONOFF\r')
    s.settimeout(5.0)  # 5 seconds
    data = s.recv(BUFFER_SIZE)
    s.settimeout(None)
    s.close()
    state = 'OFF'
    print data
    print data[13]
    if data[13] == "F":
        state = 'OFF'
    else:
        state = 'ON'
    return state


if __name__ == '__main__':
    test_response = requests.get(PUBLIC_RESOURCES)
    if test_response.status_code != 200:
        # Don't! If you catch, likely to hide bugs.
        raise Exception('Service not still running')
    scan_register()
    app.run(debug=True, host='0.0.0.0', port=3030)
