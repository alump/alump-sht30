import smbus2
import json
from datetime import datetime, timezone
import os
import requests
import time
import statistics

def roundPartial(val, res):
    return round(val * res) / res

URL = 'http://supervisor/core/api/states/'

bus = smbus2.SMBus(1)
lastTemp = -300.0
lastHum = -1.0
lastTempUpdate = datetime(2024, 1, 1, 0, 0)
lastHumUpdate = datetime(2024, 1, 1, 0, 0)

statTempSamples = []
statHumSamples = []

while True:
    loopStart = datetime.now(timezone.utc)
    tempSamples = []
    humSamples = []
    
    for x in range(0, 20):
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        data = bus.read_i2c_block_data(0x44, 0x00, 6)
        sampleTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        tempSamples.append(sampleTemp)
        statTempSamples.append(statTempSamples)
        sampleHum = 100 * (data[3] * 256 + data[4]) / 65535.0
        humSamples.append(sampleHum)
        statHumSamples.append(statTempSamples)
        time.sleep(1)
    
    cTemp = round(statistics.harmonic_mean(tempSamples), 1)
    humidity = round(statistics.harmonic_mean(humSamples), 1)

    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()
    token = os.environ.get('SUPERVISOR_TOKEN','?')
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + token }
    
    tempTimeDelta = (now - lastTempUpdate)
    if lastTemp != cTemp or tempTimeDelta.total_seconds() > 300:
        entityId = 'sensor.sht30_temperature'
        url = URL + entityId
        data = {'attributes': { 'friendly_name': 'Local Temperature (SHT30)', 'unit_of_measurement': '\N{DEGREE SIGN}C'}}
        data['entity'] = entityId
        data['state'] = cTemp
        data['last_updated'] = timestamp
        data['attributes']['stdev'] = round(statistics.stdev(statTempSamples), 3)
        data['attributes']['min'] = round(min(statTempSamples), 3)
        data['attributes']['max'] = round(max(statTempSamples), 3)
        data['attributes']['samples'] = len(statTempSamples)
        if lastTemp > -274:
            data['attributes']['delta'] = cTemp - lastTemp
            data['attributes']['seconds'] = tempTimeDelta
        response = requests.post(url, data=json.dumps(data), headers=headers)
        lastTemp = cTemp
        lastTempUpdate = now
        statTempSamples = []
    
    humTimeDelta = (now - lastHumUpdate)
    if lastHum != humidity or humTimeDelta.total_seconds() > 300:
        entityId = 'sensor.sht30_humidity'
        url = URL + entityId
        data = {'attributes': { 'friendly_name': 'Local Relative Humidity (SHT30)', 'unit_of_measurement': '%'}}
        data['entity'] = entityId
        data['state'] = humidity
        data['last_updated'] = timestamp
        data['attributes']['stdev'] = round(statistics.stdev(statHumSamples), 3)
        data['attributes']['min'] = round(min(statHumSamples), 3)
        data['attributes']['max'] = round(max(statHumSamples), 3)
        data['attributes']['samples'] = len(statHumSamples)
        if lastHum >= 0 and lastHum <= 100:
           data['attributes']['delta'] = humidity - lastHum
           data['attributes']['seconds'] = humTimeDelta
        response = requests.post(url, data=json.dumps(data), headers=headers)
        lastHum = humidity
        lastHumUpdate = now
        statHumSamples = []
    
    idleTime = 60 - (datetime.now(timezone.utc) - loopStart).total_seconds()
    time.sleep(idleTime)
