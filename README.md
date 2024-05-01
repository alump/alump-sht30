# SHT30 Addon for Home Assistant

Add-on for Home Assistant OS running on Raspberry PI with SHT30 i2C sensor. You need to enable i2c access
to use this add-on.

Updates sensor.sht30_temperature and sensor.sht30_humidity entities with current values every X seconds

## TODO features
- Configuration. Either by UI, or at least configuration file.
- Sampling amount and frequency and amount of decimals to config
- Maybe support for Fahrenheit.
- Support for second i2c port, other devices?
- Better logging
- Code split, allow to run this on also on an another raspberry pi

## Installation

### Attach SHT30 to Raspberry Pi

Connect SHT30 to Raspberry Pi by using pins 3-6.
White = 3 (SDA)
Red = 4 (5V)
Yellow = 5 (SCL)
Black = 6 (GND)

### Enable i2c

Follow [this guide](https://community.home-assistant.io/t/add-on-hassos-i2c-configurator/264167]). Many steps, many restarts needed.

Once HassOS i2c configutor says that all is ready, move to next step.

### Copy this addon to filesystem

- git clone this repository to /addons
- restart whole device
- Under "settings -> addons -> store -> local" you should see this addon, install it
- Start the addon
- Inspect the logs, if no issues, try to find the generated entity sht30.temperature
