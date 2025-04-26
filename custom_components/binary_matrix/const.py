"""Constants for the Binary Matrix 8x8 HDMI Switcher integration."""
from typing import Final

DOMAIN: Final = "binary_matrix"

# Configuration
CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_PORT = 23
DEFAULT_USERNAME = "admin"
DEFAULT_SCAN_INTERVAL = 30

# Commands
CMD_STMAP = "STMAP"
CMD_QUIT = "q"

# Services
SERVICE_SWITCH_INPUT = "switch_input"
SERVICE_SET_MAPPING = "set_mapping"

# Attributes
ATTR_OUTPUT = "output"
ATTR_INPUT = "input"
ATTR_MAPPING = "mapping"
ATTR_CONNECTION_STATE = "connection_state"

# State
STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"
STATE_ERROR = "error"

# Matrix Size
MATRIX_SIZE = 8
OUTPUT_RANGE = range(1, MATRIX_SIZE + 1)
INPUT_RANGE = range(1, MATRIX_SIZE + 1)

# Error Messages
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_AUTH = "invalid_auth"
ERROR_UNKNOWN = "unknown"