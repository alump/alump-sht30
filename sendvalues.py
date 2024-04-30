import smbus2
import json
import datetime
import os
import requests
import time

bus = smbus2.SMBus(1)
lastTemp = -300.0
lastHum = -1.0

while True:
    tempSum = 0.0
    humSum = 0.0
    
    for x in range(0, 5):
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        data = bus.read_i2c_block_data(0x44, 0x00, 6)
        tempSum += ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        humSum += 100 * (data[3] * 256 + data[4]) / 65535.0
        time.sleep(2)
    
    cTemp = round(tempSum / 5.0, 1)
    humidity = round(humSum / 5.0)
    timestamp = datetime.datetime.utcnow().isoformat()
    token = os.environ.get('SUPERVISOR_TOKEN','?')
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + token }
    
    if lastTemp != cTemp:
        url = 'http://supervisor/core/api/states/sensor.sht30_temperature'
        data = {'entity': 'sensor.sht30_temperature', 'attributes': { 'unit_of_measurement': '\N{DEGREE SIGN}C'}}
        data['state'] = cTemp
        data['last_updated'] = timestamp
        response = requests.post(url, data=json.dumps(data), headers=headers)
        lastTemp = cTemp
    
    if lastHum != humidity:
        url = 'http://supervisor/core/api/states/sensor.sht30_humidity'
        data = {'entity': 'sensor.sht30_humidity', 'attributes': { 'unit_of_measurement': '%'}}
        data['state'] = humidity
        data['last_updated'] = timestamp
        response = requests.post(url, data=json.dumps(data), headers=headers)
        lastHum = humidity
    
    time.sleep(50)
