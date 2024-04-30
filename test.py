from sht20 import SHT20
sht = SHT20(1, resolution=SHT20.TEMP_RES_14bit)
temp = sht.read_temp()
humid = sht.read_humid()
print("Temperature (°C): " + str(temp))
print("Humidity (%RH): " + str(humid))
