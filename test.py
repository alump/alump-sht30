import smbus2

bus = smbus2.SMBus(1)
bus.write_i2c_block_data(0x44, 0x2C, [0x06])
data = bus.read_i2c_block_data(0x44, 0x00, 6)
cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

hStr = 'Relative humidity: {:.2f} %'.format(humidity)
tStr = 'Temperature: {:.2f} \N{DEGREE SIGN}C'.format(cTemp)
print(hStr)
print(tStr)
