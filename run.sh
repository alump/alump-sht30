#!/usr/bin/with-contenv bashio

echo "SHT30 starting..."
python3 test.py
python3 sendvalues.py
