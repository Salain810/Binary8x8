"""Constants for Binary Matrix integration."""
from datetime import timedelta
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
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)
DEFAULT_TIMEOUT = 10.0
DEFAULT_RECONNECT_DELAY = 5.0

# Commands
CMD_STMAP = "STMAP"
CMD_QUIT = "q"

# Services
SERVICE_SWITCH_INPUT = "switch_input"

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

# Debug Flags
DEBUG_TELNET = True
DEBUG_RESPONSE_DUMP = True
DEBUG_STATE_UPDATES = True

# Connection Settings
CONNECTION_RETRY_ATTEMPTS = 3
COMMAND_RETRY_ATTEMPTS = 2
READ_CHUNK_SIZE = 1024
INITIAL_CONNECT_TIMEOUT = 15.0
COMMAND_TIMEOUT = 5.0
AUTH_TIMEOUT = 8.0
STATE_UPDATE_TIMEOUT = 10.0

# Response Markers
LOGIN_PROMPT = "Login:"
PASSWORD_PROMPT = "Password:"
PROMPT_MARKER = ">"
SUCCESS_MARKER = "Logged in successfully"