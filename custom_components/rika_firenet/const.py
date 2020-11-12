from homeassistant.components.climate.const import (PRESET_AWAY,
                                                    PRESET_HOME)

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
PLATFORMS = [CLIMATE, SENSOR]

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
