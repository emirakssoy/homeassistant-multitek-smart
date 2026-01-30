"""Constants for Multitek Smart Home integration."""
from typing import Final

DOMAIN: Final = "multitek_smart"

# Configuration keys
CONF_TABLET_IP = "tablet_ip"
CONF_TABLET_PORT = "tablet_port"
CONF_API_KEY = "api_key"
CONF_USE_AUTH = "use_auth"

# Default values
DEFAULT_PORT = 8123
DEFAULT_UPDATE_INTERVAL = 30  # seconds

# Device types - matching Android SmartConstants
RELAY_TYPE_LIGHT = 1
RELAY_TYPE_SHUTTER = 2
RELAY_TYPE_ON_OFF = 3
RELAY_TYPE_GAS = 4
RELAY_TYPE_ELECTRIC = 5
RELAY_TYPE_WATER = 6

# API Endpoints
API_STATUS = "/api/status"
API_DEVICES = "/api/devices"
API_DEVICE = "/api/device/{device_id}"
API_RELAY_LIST = "/api/relay/list"
API_RELAY_STATE = "/api/relay/{device_id}/state"
API_RELAY_TOGGLE = "/api/relay/{device_id}/toggle"
API_DISCOVER = "/api/discover"

# Attributes
ATTR_DEVICE_TYPE = "device_type"
ATTR_ROOM_ID = "room_id"
ATTR_ROOM_NAME = "room_name"
ATTR_FLAT_ID = "flat_id"
ATTR_FLAT_NAME = "flat_name"
ATTR_FAVOURITE = "favourite"
ATTR_REVERSE_CONTACT = "reverse_contact"

# Device type icons
DEVICE_TYPE_ICONS = {
    RELAY_TYPE_LIGHT: "mdi:lightbulb",
    RELAY_TYPE_SHUTTER: "mdi:window-shutter",
    RELAY_TYPE_ON_OFF: "mdi:toggle-switch",
    RELAY_TYPE_GAS: "mdi:gas-cylinder",
    RELAY_TYPE_ELECTRIC: "mdi:flash",
    RELAY_TYPE_WATER: "mdi:water",
}

# Device type names
DEVICE_TYPE_NAMES = {
    RELAY_TYPE_LIGHT: "Light",
    RELAY_TYPE_SHUTTER: "Shutter",
    RELAY_TYPE_ON_OFF: "Switch",
    RELAY_TYPE_GAS: "Gas Valve",
    RELAY_TYPE_ELECTRIC: "Electric Switch",
    RELAY_TYPE_WATER: "Water Valve",
}
