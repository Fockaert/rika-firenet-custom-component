import logging

from homeassistant.components.switch import SwitchEntity

from .entity import RikaFirenetEntity

from .const import (
    DOMAIN
)
from .core import RikaFirenetCoordinator
from .core import RikaFirenetStove

_LOGGER = logging.getLogger(__name__)

DEVICE_SWITCH = [
    "on off",
    "convection fan1",
    "convection fan2"
]


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.info("setting up platform switches")
    coordinator: RikaFirenetCoordinator = hass.data[DOMAIN][entry.entry_id]

    stove_entities = []

    # Create stove switches
    for stove in coordinator.get_stoves():
        stove_entities.extend(
            [
                RikaFirenetStoveBinarySwitch(entry, stove, coordinator, number)
                for number in DEVICE_SWITCH
            ]
        )
    if stove_entities:
        async_add_entities(stove_entities, True)


class RikaFirenetStoveBinarySwitch(RikaFirenetEntity, SwitchEntity):
    def __init__(self, config_entry, stove: RikaFirenetStove, coordinator: RikaFirenetCoordinator, number):
        super().__init__(config_entry, stove, coordinator, number)

        self._number = number

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        _LOGGER.info("async_turn_on " + self._number)

        if self._number == "on off":
            self._stove.turn_on()
        elif self._number == "convection fan1":
            self._stove.turn_convection_fan1_on()
        elif self._number == "convection fan2":
            self._stove.turn_convection_fan2_on()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        _LOGGER.info("async_turn_off " + self._number)

        if self._number == "on off":
            self._stove.turn_off()
        elif self._number == "convection fan1":
            self._stove.turn_convection_fan1_off()
        elif self._number == "convection fan2":
            self._stove.turn_convection_fan2_off()

    @property
    def icon(self):
        return "hass:power"

    @property
    def is_on(self):
        if self._number == "on off":
            return self._stove.is_stove_on()
        elif self._number == "convection fan1":
            return self._stove.is_stove_convection_fan1_on()
        elif self._number == "convection fan2":
            return self._stove.is_stove_convection_fan2_on()
