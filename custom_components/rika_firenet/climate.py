import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (HVAC_MODE_AUTO,
													HVAC_MODE_HEAT,
													HVAC_MODE_OFF,
													SUPPORT_TARGET_TEMPERATURE)
from homeassistant.const import (ATTR_TEMPERATURE, TEMP_CELSIUS)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (DOMAIN,
					SIGNAL_RIKA_FIRENET_UPDATE_RECEIVED, SUPPORT_PRESET)
from .core import RikaFirenetConnector, RikaFirenetStove

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE  # | SUPPORT_PRESET_MODE

# from the remote control and gree app
MIN_TEMP = 16
MAX_TEMP = 30

# fixed values in gree mode lists
HVAC_MODES = [HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_OFF]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up platform."""
    _LOGGER.info("setting up platform climate")
    # _LOGGER.info("data from domain" + str(hass.data[DOMAIN]))
    connector: RikaFirenetConnector = hass.data[DOMAIN][entry.entry_id]

    stove_entities = []

    # Create stove sensors
    for stove in connector.get_stoves():
        stove_entities.append(RikaFirenetStoveClimate(stove))

    if stove_entities:
        async_add_entities(stove_entities, True)


class RikaFirenetStoveClimate(ClimateEntity):
    """Representation of an RikaStove."""

    def __init__(self, stove: RikaFirenetStove):
        """Initialize of the Tado Sensor."""
        self._id = stove.get_id()
        self._name = stove.get_name()
        self._stove = stove
        self.device_id = self._id
        self._unique_id = self._id

    async def async_added_to_hass(self):
        """Register for sensor updates."""

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_RIKA_FIRENET_UPDATE_RECEIVED.format(
                    self.device_id
                ),
                self._async_update_callback,
            )
        )
        self._async_update_device_data()

    @callback
    def _async_update_callback(self):
        """Update and write state."""
        _LOGGER.info("_async_update_callback()")
        self._async_update_device_data()
        self.async_write_ha_state()

    @callback
    def _async_update_device_data(self):
        """Handle update callbacks."""

    # _LOGGER.info("new state: " + str(self._state))

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def current_temperature(self):
        temp = self._stove.get_room_temperature()
        _LOGGER.info('current_temperature(): ' + str(temp))
        return temp

    @property
    def min_temp(self):
        return MIN_TEMP

    @property
    def max_temp(self):
        return MAX_TEMP

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return SUPPORT_PRESET

    def set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        self._stove.set_presence(preset_mode)

    @property
    def target_temperature(self):
        temp = self._stove.get_room_thermostat()
        _LOGGER.info('target_temperature()): ' + str(temp))
        # Return the supported step of target temperature.
        return temp

    @property
    def target_temperature_step(self):
        return 1

    @property
    def hvac_mode(self):
        return self._stove.get_hvac_mode()

    @property
    def hvac_modes(self):
        return HVAC_MODES

    def set_hvac_mode(self, hvac_mode):
        _LOGGER.info('set_hvac_mode()): ' + str(hvac_mode))
        self._stove.set_hvac_mode(str(hvac_mode))

    @property
    def supported_features(self):
        return SUPPORT_FLAGS

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    def set_temperature(self, **kwargs):
        temperature = int(kwargs.get(ATTR_TEMPERATURE))
        _LOGGER.info('set_temperature(): ' + str(temperature))

        if kwargs.get(ATTR_TEMPERATURE) is None:
            return

        if not self._stove.is_stove_on():
            return

        # do nothing if HVAC is switched off
        self._stove.set_stove_temperature(temperature)
        self.schedule_update_ha_state()
