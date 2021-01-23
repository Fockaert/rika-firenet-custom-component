import logging

from homeassistant.const import PERCENTAGE
from .entity import RikaFirenetEntity
from homeassistant.components.number import NumberEntity

from .const import (
    DOMAIN
)
from .core import RikaFirenetCoordinator
from .core import RikaFirenetStove

_LOGGER = logging.getLogger(__name__)

DEVICE_NUMBERS = [
    "room power request",
    "heating power"
]

async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.info("setting up platform number")
    coordinator: RikaFirenetCoordinator = hass.data[DOMAIN][entry.entry_id]

    stove_entities = []

    # Create stove numbers
    for stove in coordinator.get_stoves():
        stove_entities.extend(
            [
                RikaFirenetStoveNumber(entry, stove, coordinator, number)
                for number in DEVICE_NUMBERS
            ]
        )

    if stove_entities:
        async_add_entities(stove_entities, True)


class RikaFirenetStoveNumber(RikaFirenetEntity, NumberEntity):
    def __init__(self, config_entry, stove: RikaFirenetStove, coordinator: RikaFirenetCoordinator, number):
        super().__init__(config_entry, stove, coordinator, number)

        self._number = number

    @property
    def min_value(self) -> float:
        if self._number == "room power request":
            return 1

        return 0

    @property
    def max_value(self) -> float:
        if self._number == "room power request":
            return 4

        return 100

    @property
    def step(self) -> float:
        if self._number == "room power request":
            return 1

        return 10

    @property
    def value(self):
        if self._number == "room power request":
            _LOGGER.info("value " + self._number + " " + str(self._stove.get_room_power_request()))
            return self._stove.get_room_power_request()
        elif self._number == "heating power":
            _LOGGER.info("value " + self._number + " " + str(self._stove.get_heating_power()))
            return self._stove.get_heating_power()

    @property
    def unit_of_measurement(self):
        if self._number == "heating power":
            return PERCENTAGE

    @property
    def icon(self):
        return "mdi:speedometer"

    def set_value(self, value: float) -> None:
        _LOGGER.info("set_value " + self._number + " " + str(value))

    async def async_set_value(self, value: float) -> None:
        _LOGGER.info("async_set_value " + self._number + " " + str(value))

        if self._number == "room power request":
            self._stove.set_room_power_request(value)
        elif self._number == "heating power":
            self._stove.set_heating_power(value)
