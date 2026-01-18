from homeassistant.components.climate.const import PRESET_AWAY, PRESET_HOME

# Configuration
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DEFAULT_TEMPERATURE = "defaultTemperature"
DATA = "data"
UPDATE_TRACK = "update_track"

# Platforms
CLIMATE = "climate"
SENSOR = "sensor"
SWITCH = "switch"
NUMBER = "number"
PLATFORMS = [CLIMATE, SENSOR, SWITCH, NUMBER]

# Types
SUPPORT_PRESET = [PRESET_AWAY, PRESET_HOME]

VERSION = "0.0.1"
DOMAIN = "rika_firenet"

UNIQUE_ID = "unique_id"

DEFAULT_NAME = "Rika"
NAME = "Rika Firenet"

UPDATE_LISTENER = "update_listener"
ISSUE_URL = "https://github.com/fockaert/rika-firenet-custom-component/issues"

# Defaults
STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# HTTP Configuration
HTTP_TIMEOUT = 10  # seconds
HTTP_RETRY_DELAY = 2  # seconds
HTTP_RETRY_MAX_ATTEMPTS = 10

# Stove States
STOVE_STATE_OFF = 1
STOVE_STATE_RUNNING = 4
STOVE_STATE_HEATING = 5

# API URLs
API_BASE_URL = "https://www.rika-firenet.com"
API_LOGIN_URL = f"{API_BASE_URL}/web/login"
API_STOVES_URL = f"{API_BASE_URL}/web/summary"
API_CLIENT_URL = f"{API_BASE_URL}/api/client"
