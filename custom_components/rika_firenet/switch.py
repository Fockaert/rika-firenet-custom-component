import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity

from .entity import RikaFirenetEntity

from .const import (
    DOMAIN
)
from .core import RikaFirenetCoordinator
from .core import RikaFirenetStove

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.info("setting up platform sensor")
    coordinator: RikaFirenetCoordinator = hass.data[DOMAIN][entry.entry_id]

    stove_entities = []

    # Create stove sensors
    for stove in coordinator.get_stoves():
        stove_entities.append(RikaFirenetStoveBinarySwitch(entry, stove, coordinator))

    if stove_entities:
        async_add_entities(stove_entities, True)


class RikaFirenetStoveBinarySwitch(RikaFirenetEntity, SwitchEntity):
    def __init__(self, config_entry, stove: RikaFirenetStove, coordinator: RikaFirenetCoordinator):
        super().__init__(config_entry, stove, coordinator)

    def turn_on(self, **kwargs: Any) -> None:
        self._stove.turn_on()

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        self._stove.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        self._stove.turn_off()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        self._stove.turn_off()

    @property
    def icon(self):
        return "hass:power"

    @property
    def is_on(self):
        return self._stove.is_stove_on()
