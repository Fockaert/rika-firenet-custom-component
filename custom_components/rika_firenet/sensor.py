import logging

from homeassistant.const import TEMP_CELSIUS, TIME_HOURS, MASS_KILOGRAMS
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEFAULT_NAME,
    DOMAIN
)
from .core import RikaFirenetCoordinator
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
    coordinator: RikaFirenetCoordinator = hass.data[DOMAIN][entry.entry_id]

    stove_entities = []

    # Create stove sensors
    for stove in coordinator.get_stoves():
        stove_entities.extend(
            [
                RikaFirenetStoveSensor(stove, coordinator, sensor)
                for sensor in DEVICE_SENSORS
            ]
        )

    if stove_entities:
        async_add_entities(stove_entities, True)


class RikaFirenetStoveSensor(CoordinatorEntity):
    def __init__(self, stove: RikaFirenetStove, coordinator: RikaFirenetCoordinator, sensor):
        self._id = stove.get_id()
        self._name = stove.get_name()
        self._stove = stove
        self._sensor = sensor
        self.device_id = self._id

        self._unique_id = f"{sensor} {self._name}"
        super().__init__(coordinator)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return f"{self._name} {self._sensor}"

    @property
    def state(self):
        if self._sensor == "stove consumption":
            return self._stove.get_stove_consumption()
        elif self._sensor == "stove runtime":
            return self._stove.get_stove_runtime()
        elif self._sensor == "stove temperature":
            return self._stove.get_stove_temperature()
        elif self._sensor == "stove thermostat":
            return self._stove.get_stove_thermostat()
        elif self._sensor == "stove burning":
            return self._stove.is_stove_burning()
        elif self._sensor == "stove status":
            return self._stove.get_status_text()
        elif self._sensor == "room temperature":
            return self._stove.get_room_temperature()
        elif self._sensor == "room thermostat":
            return self._stove.get_room_thermostat()
        elif self._sensor == "room power request":
            return self._stove.get_room_power_request()

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
