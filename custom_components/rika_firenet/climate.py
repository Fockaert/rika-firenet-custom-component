import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature

from homeassistant.const import (ATTR_TEMPERATURE, UnitOfTemperature)

from .const import (DOMAIN, SUPPORT_PRESET)
from .core import RikaFirenetCoordinator
from .entity import RikaFirenetEntity
from .exceptions import RikaValidationError

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = ClimateEntityFeature.TARGET_TEMPERATURE  # | SUPPORT_PRESET_MODE

MIN_TEMP = 16
MAX_TEMP = 30

HVAC_MODES = [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up platform."""
    _LOGGER.info("setting up platform climate")
    coordinator: RikaFirenetCoordinator = hass.data[DOMAIN][entry.entry_id]

    stove_entities = []

    # Create stove sensors
    for stove in coordinator.get_stoves():
        stove_entities.append(RikaFirenetStoveClimate(entry, stove, coordinator))

    if stove_entities:
        async_add_entities(stove_entities, True)


class RikaFirenetStoveClimate(RikaFirenetEntity, ClimateEntity):

    @property
    def current_temperature(self):
        temp = self._stove.get_room_temperature()
        _LOGGER.debug('current_temperature(): %s', temp)
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
        self.schedule_update_ha_state()

    @property
    def target_temperature(self):
        temp = self._stove.get_room_thermostat()
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
        _LOGGER.debug('set_hvac_mode(): %s', hvac_mode)
        self._stove.set_hvac_mode(str(hvac_mode))
        self.schedule_update_ha_state()

    @property
    def supported_features(self):
        return SUPPORT_FLAGS

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    def set_temperature(self, **kwargs):
        if kwargs.get(ATTR_TEMPERATURE) is None:
            _LOGGER.warning("Temperature value not provided")
            return

        if not self._stove.is_stove_on():
            _LOGGER.debug("Stove is off, skipping temperature change")
            return

        temperature = float(kwargs.get(ATTR_TEMPERATURE))

        # Validate temperature range
        if temperature < MIN_TEMP or temperature > MAX_TEMP:
            _LOGGER.error(
                "Temperature %s out of range [%s, %s]",
                temperature, MIN_TEMP, MAX_TEMP
            )
            raise RikaValidationError(
                f"Temperature {temperature} out of valid range [{MIN_TEMP}, {MAX_TEMP}]"
            )

        _LOGGER.debug('set_temperature(): %s', temperature)
        self._stove.set_stove_temperature(int(temperature))
        self.schedule_update_ha_state()
