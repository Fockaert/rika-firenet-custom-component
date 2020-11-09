import logging

from homeassistant.const import TEMP_CELSIUS, TIME_HOURS, MASS_KILOGRAMS
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import (
	DEFAULT_NAME,
	DOMAIN,
	SIGNAL_RIKA_FIRENET_UPDATE_RECEIVED
)
from .core import RikaFirenetConnector
from .core import RikaFirenetStove

_LOGGER = logging.getLogger(__name__)

DEVICE_SENSORS = [
    "stove consumption",
    "stove runtime",
    "stove temperature",
    "stove thermostat",
    "stove burning",
    "stove status",
    "room temperature",
    "room thermostat",
    "room power request",
]


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.info("setting up platform sensor")
    connector: RikaFirenetConnector = hass.data[DOMAIN][entry.entry_id]

    stove_entities = []

    # Create stove sensors
    for stove in connector.get_stoves():
        stove_entities.extend(
            [
                RikaFirenetStoveSensor(stove, sensor)
                for sensor in DEVICE_SENSORS
            ]
        )

    if stove_entities:
        async_add_entities(stove_entities, True)


class RikaFirenetStoveSensor(Entity):
    def __init__(self, stove: RikaFirenetStove, sensor):
        self._id = stove.get_id()
        self._name = stove.get_name()
        self._stove = stove
        self._sensor = sensor
        self._state = None
        self.device_id = self._id

        self._unique_id = f"{sensor} {self._name}"

    async def async_added_to_hass(self):
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

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return f"{self._name} {self._sensor}"

    @property
    def state(self):
        return self._state

    @callback
    def _async_update_callback(self):
        _LOGGER.info("_async_update_callback()")
        self._async_update_device_data()
        self.async_write_ha_state()

    @callback
    def _async_update_device_data(self):
        if self._sensor == "stove consumption":
            self._state = self._stove.get_stove_consumption()
        elif self._sensor == "stove runtime":
            self._state = self._stove.get_stove_runtime()
        elif self._sensor == "stove temperature":
            self._state = self._stove.get_stove_temperature()
        elif self._sensor == "stove thermostat":
            self._state = self._stove.get_stove_thermostat()
        elif self._sensor == "stove burning":
            self._state = self._stove.is_stove_burning()
        elif self._sensor == "stove status":
            self._state = self._stove.get_status_text()
        elif self._sensor == "room temperature":
            self._state = self._stove.get_room_temperature()
        elif self._sensor == "room thermostat":
            self._state = self._stove.get_room_thermostat()
        elif self._sensor == "room power request":
            self._state = self._stove.get_room_power_request()

        _LOGGER.info("new state: " + str(self._state))

    @property
    def unit_of_measurement(self):
        if "temperature" in self._sensor or "thermostat" in self._sensor:
            return TEMP_CELSIUS
        elif self._sensor == "stove consumption":
            return MASS_KILOGRAMS
        elif self._sensor == "stove runtime":
            return TIME_HOURS

    @property
    def icon(self):
        if "temperature" in self._sensor or "thermostat" in self._sensor:
            return "mdi:thermometer"
        elif self._sensor == "stove consumption":
            return "mdi:weight-kilogram"
        elif self._sensor == "stove runtime":
            return "mdi:timelapse"
        elif self._sensor == "stove burning":
            return "mdi:fire"
        elif self._sensor == "stove status":
            return "mdi:information-outline"

    @property
    def device_info(self):
        info = {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._id,
            "manufacturer": DEFAULT_NAME,
            "model": DEFAULT_NAME,
        }
        _LOGGER.info("info:" + str(info))
        return info
