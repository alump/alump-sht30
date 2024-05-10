#!/usr/bin/with-contenv bashio

echo "Testing SHT30..."
python3 test.py
echo "Starting SHT30..."
python3 sendvalues.py
