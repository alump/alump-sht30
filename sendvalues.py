import smbus2
import json
import datetime
import os

bus = smbus2.SMBus(1)
bus.write_i2c_block_data(0x44, 0x2C, [0x06])
data = bus.read_i2c_block_data(0x44, 0x00, 6)
cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
timestamp = datetime.datetime.utcnow().isoformat()

token = os.environ.get('SUPERVISOR_TOKEN','?')

print('Sending Temperature: {:.2f} \N{DEGREE SIGN}C'.format(cTemp))
url = 'http://supervisor/core/api/states/sensor.sht30_temperature'
headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + token }
data = {'entity': 'sensor.sht30_temperature', 'attributes': { 'unit_of_measurement': '\N{DEGREE SIGN}C'}}
data['state'] = cTemp
data['last_updated'] = timestamp
response = requests.post(url, data=json.dumps(data), headers=headers)

print('Swnding humidity: {:.2f} %'.format(humidity))
url = 'http://supervisor/core/api/states/sensor.sht30_humidity'
data = {'entity': 'sensor.sht30_humidity', 'attributes': { 'unit_of_measurement': '%'}
data['state'] = cTemp
data['last_updated'] = timestamp
response = requests.post(url, data=json.dumps(data), headers=headers)
