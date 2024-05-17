#!/usr/bin/with-contenv bashio
set -e

export CONFIG_TEMPERATURE_ENTITY_ID=$(bashio::config 'temperature_entity_id')
export CONFIG_TEMPERATURE_FRIENDLY_NAME=$(bashio::config 'temperature_friendly_name')
export CONFIG_HUMIDITY_ENTITY_ID=$(bashio::config 'humidity_entity_id')
export CONFIG_HUMIDITY_FRIENDLY_NAME=$(bashio::config 'humidity_friendly_name')
export CONFIG_SEND_INTERVAL=$(bashio::config 'send_interval')
export CONFIG_SAMPLES=$(bashio::config 'samples')
export CONFIG_TEMPERATURE_DECIMALS=$(bashio::config 'temperature_decimals')
export CONFIG_HUMIDITY_DECIMALS=$(bashio::config 'humidity_decimals')
