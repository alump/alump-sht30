import smbus2
import json
import datetime
import os
import requests
import time

bus = smbus2.SMBus(1)
lastTemp = -300.0
lastHum = -1.0
lastTempUpdate = datetime.datetime(2024, 1, 1, 0, 0)
lastHumUpdate = datetime.datetime(2024, 1, 1, 0, 0)

while True:
    loopStart = datetime.datetime.utcnow()
    tempSum = 0.0
    humSum = 0.0
    
    for x in range(0, 5):
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        data = bus.read_i2c_block_data(0x44, 0x00, 6)
        tempSum += ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        humSum += 100 * (data[3] * 256 + data[4]) / 65535.0
        time.sleep(1)
    
    cTemp = round(tempSum / 5.0, 2)
    humidity = round(humSum / 5.0, 1)
    now = datetime.datetime.utcnow()
    timestamp = now.isoformat()
    token = os.environ.get('SUPERVISOR_TOKEN','?')
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + token }
    
    tempTimeDelta = (now - lastTempUpdate)
    if lastTemp != cTemp or tempTimeDelta.total_seconds() > 300:
        url = 'http://supervisor/core/api/states/sensor.sht30_temperature'
        data = {'entity': 'sensor.sht30_temperature', 'attributes': { 'friendly_name': 'SHT30 Temperature', 'unit_of_measurement': '\N{DEGREE SIGN}C'}}
        data['state'] = cTemp
        data['last_updated'] = timestamp
        response = requests.post(url, data=json.dumps(data), headers=headers)
        lastTemp = cTemp
        lastTempUpdate = now
    
    humTimeDelta = (now - lastHumUpdate)
    if lastHum != humidity or humTimeDelta.total_seconds() > 300:
        url = 'http://supervisor/core/api/states/sensor.sht30_humidity'
        data = {'entity': 'sensor.sht30_humidity', 'attributes': { 'friendly_name': 'SHT30 Relative Humidity', 'unit_of_measurement': '%'}}
        data['state'] = humidity
        data['last_updated'] = timestamp
        response = requests.post(url, data=json.dumps(data), headers=headers)
        lastHum = humidity
        lastHumUpdate = now
    
    idleTime = 60 - (datetime.datetime.utcnow() - loopStart).total_seconds()
    time.sleep(idleTime)
