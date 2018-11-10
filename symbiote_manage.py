import ctypes
import json
from ctypes import c_char_p
from time import sleep
import requests

LIBLWSP = 'dist/libLWSPLibrary.so'
lib = ctypes.CDLL(LIBLWSP)

lib.sendSDEVHelloToGW.restype = ctypes.c_char_p
lib.sendAuthN.restype = ctypes.c_char_p
lib.getDK1.restype = ctypes.c_char_p
lib.preparePacket.restype = ctypes.c_char_p
lib.decryptPacketFromInnk.restype = ctypes.c_char_p

# SSP_URL = 'innkeeper.symbiote.org'
SSP_URL = 'localhost'
SSP_PORT = '8081'
URL_REGISTER = 'http://' + SSP_URL + ':' + SSP_PORT + '/innkeeper/sdev/register'
URL_JOIN = 'http://' + SSP_URL + ':' + SSP_PORT + '/innkeeper/sdev/join'
URL_UNREGISTER = 'http://' + SSP_URL + ':' + \
    SSP_PORT + '/innkeeper/sdev/unregister'
URL_KEEPALIVE = 'http://' + SSP_URL + ':' + \
    SSP_PORT + '/innkeeper/sdev/keepalive'


def create_LWSP_tunnel(mac_addr):
    lib.begin('sym-112233445566778899')
    mac_str = c_char_p(mac_addr.encode('utf-8'))
    json_str = c_char_p(lib.sendSDEVHelloToGW(mac_str))
    if not json_str:
        print("SDEV Hello response was empty")
        print("bye bye")
        return -1

    print("SDEV Hello string:")
    print(json_str.value)
    # Hello response to be sent with a POST request to /innkeeper/sdev/register
    innk_resp = requests.post(URL_REGISTER, data=json_str.value, headers={
                              'Content-Type': 'Application/json'})
    # Innkeeper response to be sent to elaborateInnkResp
    print("Innkeeper SDEV Hello response")
    print(innk_resp)
    innk_resp_str = c_char_p(innk_resp.text.encode('utf-8'))
    lib.elaborateInnkResp(innk_resp_str.value)
    lib.calculateDK1(4)
    lib.calculateDK2(4)
    jsonAuthStr = c_char_p(lib.sendAuthN())
    if not jsonAuthStr:
        print("Authorization response was empty")
        print("bye bye")
        return -1

    print("SDEV AuthN string:")
    print(jsonAuthStr.value)
    innk_resp = requests.post(URL_REGISTER, data=jsonAuthStr.value, headers={
                              'Content-Type': 'Application/json'})
    innk_resp = innk_resp.text.encode('utf-8')
    innk_resp_str = c_char_p(innk_resp)
    print("Innkeeper SDEV AuthN response")
    print(innk_resp_str.value)
    lib.elaborateInnkResp(innk_resp_str.value)
    dk1 = c_char_p(lib.getDK1())
    dk1_str = dk1.value
    print("DK1: ")
    print(dk1_str)

    return dk1_str


def encrypt_payload(payload):
    payload_str = c_char_p(payload.encode('utf-8'))
    encr = c_char_p(lib.preparePacket(payload_str.value))
    tmp = encr.value
    idx = tmp.rfind("}")
    encr_str = tmp[0:idx + 1]
    print("SDEV encrypted message:")
    print(encr_str)

    return encr_str


def decrypt_payload(payload):
    decrypt = c_char_p(lib.decryptPacketFromInnk(payload))
    print("SDEV decrypted message:")
    print(decrypt.value)
    tmp = decrypt.value
    idx = tmp.rfind("}")
    decrypt_str = tmp[0:idx + 1]
    print("SDEV decrypted message:")
    print(decrypt_str)

    return decrypt_str


def create_sdev_description_room_sensor(dk1_str, mac_address):
    sdev = '{ "symId": "",  "pluginId": "' + str(mac_address) + '", "sspId": "", "roaming": false, "pluginURL": "http://localhost:3030/rap/room_sensor", "dk1": "' + str(
        dk1_str) + '", "hashField": "00000000000000000000"}'
    print("SDEV description: \n" + sdev)
    return sdev


def create_sdev_description_ac_switch(dk1_str, mac_address):
    sdev = '{ "symId": "",  "pluginId": "' + str(mac_address) + '", "sspId": "", "roaming": false, "pluginURL": "http://localhost:3030/rap/ac_switch", "dk1": "' + str(
        dk1_str) + '", "hashField": "00000000000000000000"}'
    print("SDEV description: \n" + sdev)
    return sdev


def create_keepalive_message(ssp_sdev_id):
    keepalive = '{ "sspId": "' + ssp_sdev_id + '" }'
    return keepalive


def create_unregister_message(ssp_sdev_id):
    unregister = '{ "sspId": "' + ssp_sdev_id + '" }'
    return unregister


def register_resource(payload):
    encr_str = encrypt_payload(payload)
    innk_resp = requests.post(URL_JOIN, data=encr_str, headers={
                              'Content-Type': 'Application/json'})
    innk_resp = innk_resp.text.encode('utf-8')
    decr_str = decrypt_payload(innk_resp)
    print("Resource registration response:")
    print(decr_str)


def unregister_room_sensor(mac_address, Id):
    dk1_str = create_LWSP_tunnel(mac_address)
    unregister = create_unregister_message(Id)
    encr_str = encrypt_payload(unregister)
    innk_resp = requests.post(URL_UNREGISTER, data=encr_str, headers={
                              'Content-Type': 'Application/json'})
    return innk_resp


def register_room_sensor(mac_address, name):
    dk1_str = create_LWSP_tunnel(mac_address)
    sdev_descr = create_sdev_description_room_sensor(dk1_str, mac_address)
    encr_str = encrypt_payload(sdev_descr)
    print("Encrypted payload:\n " + encr_str)
    print("Registering SDEV..")
    innk_resp = requests.post(URL_REGISTER, data=encr_str, headers={
                              'Content-Type': 'Application/json'})
    if innk_resp.status_code != 200:
        print("SDEV registration ERROR: " + innk_resp.reason)
        exit(0)

    innk_resp = innk_resp.text.encode('utf-8')
    print("Innkeeper response: \n " + innk_resp)
    decr_str = decrypt_payload(innk_resp)
    print("SDEV registration response:")
    print(decr_str)
    sdev_returned = json.loads(decr_str)
    sym_id = sdev_returned["symId"]
    ssp_id = sdev_returned["sspId"]
    timeout = sdev_returned["registrationExpiration"]
    print("SDEV registration successful")

    device_name = name + '_' + mac_address

    resource_1 = str('{\
		  "internalIdResource": "' + mac_address + '",\
		  "sspIdResource": "",\
		  "sspIdParent": "' + ssp_id + '",\
		  "symIdParent": "' + sym_id + '",\
		  "accessPolicy": {\
			"policyType": "PUBLIC",\
			"requiredClaims": {}\
		  },\
		  "filteringPolicy": {\
			"policyType": "PUBLIC",\
			"requiredClaims": {}\
		  },\
		  "resource": {\
			"@c": ".StationarySensor",\
			"id": "",\
			"name": "' + device_name + '",\
			"description": ["Room_Sensor"],\
			"interworkingServiceURL": "http://localhost:3030/rap/room_sensor",\
			"locatedAt": null,\
			"services": null,\
			"observesProperty": [\
			  "temperature",\
			  "humidity",\
              "activity",\
              "batteryLevel",\
              "action"\
			]\
		  }\
		}')
    register_resource(resource_1)

    kalive = create_keepalive_message(ssp_id)
    encr_str = encrypt_payload(kalive)
    print("Start sending keepalive every " + str(timeout) + " seconds")
    innk_resp = requests.post(URL_KEEPALIVE, data=encr_str, headers={
                              'Content-Type': 'Application/json'})


def register_ac_switch(mac_address, ip_address, name):
    dk1_str = create_LWSP_tunnel(mac_address)
    sdev_descr = create_sdev_description_ac_switch(
        dk1_str, mac_address)
    encr_str = encrypt_payload(sdev_descr)
    print("Encrypted payload:\n " + encr_str)
    print("Registering SDEV..")
    innk_resp = requests.post(URL_REGISTER, data=encr_str, headers={
                              'Content-Type': 'Application/json'})
    if innk_resp.status_code != 200:
        print("SDEV registration ERROR: " + innk_resp.reason)
        exit(0)

    innk_resp = innk_resp.text.encode('utf-8')
    print("Innkeeper response: \n " + innk_resp)
    decr_str = decrypt_payload(innk_resp)
    print("SDEV registration response:")
    print(decr_str)
    sdev_returned = json.loads(decr_str)
    sym_id = sdev_returned["symId"]
    ssp_id = sdev_returned["sspId"]
    timeout = sdev_returned["registrationExpiration"]
    print("SDEV registration successful")

    device_name = name + '_' + mac_address

    resource_1 = str('{\
		  "internalIdResource": "' + ip_address + '",\
		  "sspIdResource": "",\
		  "sspIdParent": "' + ssp_id + '",\
		  "symIdParent": "' + sym_id + '",\
		  "accessPolicy": {\
			"policyType": "PUBLIC",\
			"requiredClaims": {}\
		  },\
		  "filteringPolicy": {\
			"policyType": "PUBLIC",\
			"requiredClaims": {}\
		  },\
		  "resource": {\
			"@c": ".Actuator",\
			"id": "",\
			"name": "' + device_name + '",\
			"description": ["AC_Switch"],\
			"interworkingServiceURL": "http://localhost:3030/rap/ac_switch",\
			"locatedAt": null,\
			"services": null,\
			"capabilities": [\
                {\
                    "name": "OnOffCapabililty",\
                    "parameters": [\
                    ],\
                    "effects": null\
                }\
			]\
		  }\
		}')
    register_resource(resource_1)

    kalive = create_keepalive_message(ssp_id)
    encr_str = encrypt_payload(kalive)
    print("Start sending keepalive every " + str(timeout) + " seconds")
    innk_resp = requests.post(URL_KEEPALIVE, data=encr_str, headers={
        'Content-Type': 'Application/json'})
