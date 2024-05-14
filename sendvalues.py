import smbus2
import json
from datetime import datetime, timezone
import os
import requests
import time
import statistics
import logging

def roundPartial(val, res):
    return round(val * res) / res

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

if os.environ.get('CONFIG_TEMPERATURE_ENTITY_ID','') == '':
    logger.warning('CONFIG_TEMPERATURE_ENTITY_ID not defined!')
if os.environ.get('CONFIG_TEMPERATURE_FRIENDLY_NAME','') == '':
    logger.warning('CONFIG_TEMPERATURE_FRIENDLY_NAME not defined!')
if os.environ.get('CONFIG_HUMIDITY_ENTITY_ID','') == '':
    logger.warning('CONFIG_HUMIDITY_ENTITY_ID not defined!')
if os.environ.get('CONFIG_HUMIDITY_FRIENDLY_NAME','') == '':
    logger.warning('CONFIG_HUMIDITY_FRIENDLY_NAME not defined!')
if os.environ.get('CONFIG_SEND_INTERVAL','') == '':
    logger.warning('CONFIG_SEND_INTERVAL not defined!')
if os.environ.get('CONFIG_SAMPLES','') == '':
    logger.warning('CONFIG_SAMPLES not defined!')

TEMP_ENTITY_ID = os.environ.get('CONFIG_TEMPERATURE_ENTITY_ID','sensor.sht30_temperature')
TEMP_FNAME = os.environ.get('CONFIG_TEMPERATURE_FRIENDLY_NAME','Local Temperature (SHT30)')
logger.info('Temperature id: "%s", name: "%s"...', TEMP_ENTITY_ID, TEMP_FNAME)
HUM_ENTITY_ID = os.environ.get('CONFIG_HUMIDITY_ENTITY_ID','sensor.sht30_humidity')
HUM_FNAME = os.environ.get('CONFIG_HUMIDITY_FRIENDLY_NAME','Local Relative Humidity (SHT30)')
logger.info('Humidity id: "%s", name: "%s"...', HUM_ENTITY_ID, HUM_FNAME)
SEND_INTERVAL = int(os.environ.get('CONFIG_SEND_INTERVAL','60'))
SAMPLES = int(os.environ.get('CONFIG_SAMPLES','20'))
URL = 'http://supervisor/core/api/states/'

TOKEN = os.environ.get('SUPERVISOR_TOKEN','?')
if (TOKEN == '?'):
    logger.error('Failed to reolve super visor token!')

bus = smbus2.SMBus(1)
lastTemp = -300.0
lastHum = -1.0
lastTempUpdate = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
lastHumUpdate = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)

statTempSamples = []
statHumSamples = []

while True:
    logger.info('Reading values...')
    loopStart = datetime.now(timezone.utc)
    tempSamples = []
    humSamples = []
    
    for x in range(0, SAMPLES):
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        data = bus.read_i2c_block_data(0x44, 0x00, 6)
        sampleTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        tempSamples.append(sampleTemp)
        statTempSamples.append(sampleTemp)
        sampleHum = 100 * (data[3] * 256 + data[4]) / 65535.0
        humSamples.append(sampleHum)
        statHumSamples.append(sampleHum)
        time.sleep(1)
    
    cTemp = round(statistics.harmonic_mean(tempSamples), 1)
    humidity = round(statistics.harmonic_mean(humSamples), 1)

    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + TOKEN }
    
    tempTimeDelta = (now - lastTempUpdate)
    if lastTemp != cTemp or tempTimeDelta.total_seconds() > 300:
        url = URL + TEMP_ENTITY_ID
        logger.info('Sending %s = %f to %s...', TEMP_ENTITY_ID, cTemp, url)
        data = {'attributes': { 'unit_of_measurement': '\N{DEGREE SIGN}C'}}
        data['entity'] = TEMP_ENTITY_ID
        data['state'] = cTemp
        data['last_updated'] = timestamp
        data['attributes']['friendly_name'] = TEMP_FNAME
        data['attributes']['stdev'] = round(statistics.stdev(statTempSamples), 3)
        data['attributes']['min'] = round(min(statTempSamples), 3)
        data['attributes']['max'] = round(max(statTempSamples), 3)
        data['attributes']['samples'] = len(statTempSamples)
        if lastTemp > -274:
            data['attributes']['delta'] = cTemp - lastTemp
            data['attributes']['seconds'] = tempTimeDelta.total_seconds()
        requestData = json.dumps(data)
        response = requests.post(url, data=requestData, headers=headers)
        if response.status_code == 400:
            logger.error('Received fatal response from server, killing addon')
            logger.error(requestData)
            break
        elif response.status_code < 200 and response.status_code > 299:
            logger.warning('Response response code %d', response.status_code)
        lastTemp = cTemp
        lastTempUpdate = now
        statTempSamples = []
    
    humTimeDelta = (now - lastHumUpdate)
    if lastHum != humidity or humTimeDelta.total_seconds() > 300:
        url = URL + HUM_ENTITY_ID
        logger.info('Sending %s = %f to %s...', HUM_ENTITY_ID, humidity, url)
        data = {'attributes': { 'unit_of_measurement': '%'}}
        data['entity'] = HUM_ENTITY_ID
        data['state'] = humidity
        data['last_updated'] = timestamp
        data['attributes']['friendly_name'] = HUM_FNAME
        data['attributes']['stdev'] = round(statistics.stdev(statHumSamples), 3)
        data['attributes']['min'] = round(min(statHumSamples), 3)
        data['attributes']['max'] = round(max(statHumSamples), 3)
        data['attributes']['samples'] = len(statHumSamples)
        if lastHum >= 0 and lastHum <= 100:
           data['attributes']['delta'] = humidity - lastHum
           data['attributes']['seconds'] = humTimeDelta.total_seconds()
        requestData = json.dumps(data)
        response = requests.post(url, data=requestData, headers=headers)
        if response.status_code == 400:
            logger.error('Received fatal response from server, killing addon')
            logger.info(requestData)
            break
        elif response.status_code < 200 and response.status_code > 299:
            logger.warning('Humidity response code %d', response.status_code)
        lastHum = humidity
        lastHumUpdate = now
        statHumSamples = []
    
    idleTime = SEND_INTERVAL - (datetime.now(timezone.utc) - loopStart).total_seconds()
    time.sleep(idleTime)
