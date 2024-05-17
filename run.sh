#!/usr/bin/with-contenv bashio
set -e

source ./env.sh

bashio::log.info "Testing SHT30 reading..."
python3 test.py

bashio::log.info "Starting SHT30 updater..."
bashio::log.info "Temperature entity ID: ${CONFIG_TEMPERATURE_ENTITY_ID}"
bashio::log.info "Temperature friendly name: ${CONFIG_TEMPERATURE_FRIENDLY_NAME}"
bashio::log.info "Humidity entity ID: ${CONFIG_HUMIDITY_ENTITY_ID}"
bashio::log.info "Humidity friendly name: ${CONFIG_HUMIDITY_FRIENDLY_NAME}"
bashio::log.info "Send interval (seconds): ${CONFIG_SEND_INTERVAL}"
bashio::log.info "Samples: ${CONFIG_SAMPLES}"
bashio::log.info "Temperature decimals: ${CONFIG_TEMPERATURE_DECIMALS}"
bashio::log.info "Humidity decimals: ${CONFIG_HUMIDITY_DECIMALS}"
python3 sendvalues.py
