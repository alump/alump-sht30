import smbus2
import json
import datetime
import os
import requests
import time
import statistics

bus = smbus2.SMBus(1)
lastTemp = -300.0
lastHum = -1.0
lastTempUpdate = datetime.datetime(2024, 1, 1, 0, 0)
lastHumUpdate = datetime.datetime(2024, 1, 1, 0, 0)

while True:
    loopStart = datetime.datetime.utcnow()
    tempSamples = []
    humSamples = []
    
    for x in range(0, 10):
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        data = bus.read_i2c_block_data(0x44, 0x00, 6)
        sampleTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        tempSamples.append(sampleTemp)
        sampleHum = 100 * (data[3] * 256 + data[4]) / 65535.0
        humSamples.append(sampleHum)
        time.sleep(1)
    
    cTemp = round(statistics.harmonic_mean(tempSamples), 2)
    humidity = round(statistics.harmonic_mean(humSamples), 1)

    now = datetime.datetime.utcnow()
    timestamp = now.isoformat()
    token = os.environ.get('SUPERVISOR_TOKEN','?')
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + token }
    
    tempTimeDelta = (now - lastTempUpdate)
    if lastTemp != cTemp or tempTimeDelta.total_seconds() > 300:
        entityId = 'sensor.sht30_temperature'
        url = 'http://supervisor/core/api/states/' + entityId
        data = {'attributes': { 'friendly_name': 'SHT30 Temperature', 'unit_of_measurement': '\N{DEGREE SIGN}C'}}
        data['entity'] = entityId
        data['state'] = cTemp
        data['last_updated'] = timestamp
        data['attributes']['stdev'] = round(statistics.stdev(tempSamples), 3)
        if lastTemp > -274:
            data['attributes']['delta'] = cTemp - lastTemp
        response = requests.post(url, data=json.dumps(data), headers=headers)
        lastTemp = cTemp
        lastTempUpdate = now
    
    humTimeDelta = (now - lastHumUpdate)
    if lastHum != humidity or humTimeDelta.total_seconds() > 300:
        entityId = 'sensor.sht30_humidity'
        url = 'http://supervisor/core/api/states/' + entityId
        data = {'attributes': { 'friendly_name': 'SHT30 Relative Humidity', 'unit_of_measurement': '%'}}
        data['entity'] = entityId
        data['state'] = humidity
        data['last_updated'] = timestamp
        data['attributes']['stdev'] = round(statistics.stdev(humSamples), 3)
        if lastHum >= 0 and lastHum <= 100:
	    data['attributes']['delta'] = humidity - lastHum
        response = requests.post(url, data=json.dumps(data), headers=headers)
        lastHum = humidity
        lastHumUpdate = now
    
    idleTime = 60 - (datetime.datetime.utcnow() - loopStart).total_seconds()
    time.sleep(idleTime)
