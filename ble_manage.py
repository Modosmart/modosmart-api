from bluepy.btle import Scanner
from bluepy.btle import UUID, Peripheral
import json


def scan_room_sensor():
    scanner = Scanner()
    devices = scanner.scan(5.0)

    my_devices = []
    for dev in devices:
        # print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
        for (adtype, desc, value) in dev.getScanData():
            if (value == "SM006"):
                current_device = {}
                current_device['mac_address'] = dev.addr
                current_device['name'] = value
                current_device['type'] = 'room_sensor'
                json_data = json.dumps(current_device)
                my_devices.append(current_device)
                # print "%s = %s" % (desc, value)
                print "%s" % (my_devices)
    return my_devices


def read_room_sensor(mac_address):
    p = Peripheral(mac_address)
    sensor_service_uuid = UUID('0000a000-0000-1000-8000-00805f9b34fb')
    battery_service_uuid = UUID(6159)
    device_info_service_uuid = UUID(6154)

    sensors_services = p.getServiceByUUID(sensor_service_uuid)
    battery_services = p.getServiceByUUID(battery_service_uuid)
    device_info_services = p.getServiceByUUID(device_info_service_uuid)

    temperature_uuid = UUID(10862)
    humidity_uuid = UUID(10863)
    presence_uuid = UUID('0000a001-0000-1000-8000-00805f9b34fb')
    battery_uuid = UUID(10777)
    firmware_uuid = UUID(10790)
    # Get Temperature
    temperature_reading = sensors_services.getCharacteristics(temperature_uuid)[
        0].read()
    temperature_b = bytearray()
    temperature_b.extend(temperature_reading)
    temperatre_value = (256 * temperature_b[1] + temperature_b[0]) / 100.0
    # Get Humidity
    humidity_reading = sensors_services.getCharacteristics(humidity_uuid)[
        0].read()
    humidity_b = bytearray()
    humidity_b.extend(humidity_reading)
    humidity_value = (256 * humidity_b[1] + humidity_b[0]) / 100.0
    # Get Presence
    presence_reading = sensors_services.getCharacteristics(presence_uuid)[
        0].read()
    presence_b = bytearray()
    presence_b.extend(presence_reading)
    presence_value = (256 * presence_b[1] + presence_b[0])
    # Get Battery
    battery_reading = battery_services.getCharacteristics(battery_uuid)[
        0].read()
    battery_b = bytearray()
    battery_b.extend(battery_reading)
    battery_value = (battery_b[0])
    # Get Firmware Version
    firmware_reading = device_info_services.getCharacteristics(firmware_uuid)[
        0].read()
    p.disconnect()

    current_readings = {}
    current_readings['temperature'] = temperatre_value
    current_readings['humidity'] = humidity_value
    current_readings['presence'] = presence_value
    current_readings['battery'] = battery_value
    current_readings['firmware'] = firmware_reading
    json_data = json.dumps(current_readings)
    return current_readings
