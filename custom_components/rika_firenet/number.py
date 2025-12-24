import logging

from homeassistant.const import PERCENTAGE
from .entity import RikaFirenetEntity
from homeassistant.components.number import NumberEntity

from .const import (
    DOMAIN
)
from .core import RikaFirenetCoordinator
from .core import RikaFirenetStove
from .exceptions import RikaValidationError

_LOGGER = logging.getLogger(__name__)

DEVICE_NUMBERS = [
    "room power request",
    "heating power",
    "convection fan1 level",
    "convection fan1 area",
    "convection fan2 level",
    "convection fan2 area"
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
    def native_min_value(self) -> float:
        if self._number == "room power request":
            return 1
        elif self._number == "convection fan1 level":
            return 0
        elif self._number == "convection fan1 area":
            return -30
        elif self._number == "convection fan2 level":
            return 0
        elif self._number == "convection fan2 area":
            return -30

        return 0

    @property
    def native_max_value(self) -> float:
        if self._number == "room power request":
            return 4
        elif self._number == "convection fan1 level":
            return 5
        elif self._number == "convection fan1 area":
            return 30
        elif self._number == "convection fan2 level":
            return 5
        elif self._number == "convection fan2 area":
            return 30

        return 100

    @property
    def native_step(self) -> float:
        if self._number == "room power request":
            return 1
        elif self._number == "convection fan1 level":
            return 1
        elif self._number == "convection fan1 area":
            return 1
        elif self._number == "convection fan2 level":
            return 1
        elif self._number == "convection fan2 area":
            return 1

        return 10

    @property
    def native_value(self):
        if self._number == "room power request":
            return self._stove.get_room_power_request()
        elif self._number == "heating power":
            return self._stove.get_heating_power()
        elif self._number == "convection fan1 level":
            return self._stove.get_convection_fan1_level()
        elif self._number == "convection fan1 area":
            return self._stove.get_convection_fan1_area()
        elif self._number == "convection fan2 level":
            return self._stove.get_convection_fan2_level()
        elif self._number == "convection fan2 area":
            return self._stove.get_convection_fan2_area()

    @property
    def native_unit_of_measurement(self):
        if self._number == "heating power":
            return PERCENTAGE
        elif self._number == "convection fan1 area":
            return PERCENTAGE
        elif self._number == "convection fan2 area":
            return PERCENTAGE

    @property
    def icon(self):
        return "mdi:speedometer"

    def set_native_value(self, value: float) -> None:
        # Validate value is within bounds
        min_value = self.native_min_value
        max_value = self.native_max_value

        if value < min_value or value > max_value:
            _LOGGER.error(
                "Value %s for %s out of range [%s, %s]",
                value, self._number, min_value, max_value
            )
            raise RikaValidationError(
                f"Value {value} for {self._number} out of valid range [{min_value}, {max_value}]"
            )

        _LOGGER.debug("set_value %s = %s", self._number, value)

        int_value = int(value)

        if self._number == "room power request":
            self._stove.set_room_power_request(int_value)
        elif self._number == "heating power":
            self._stove.set_heating_power(int_value)
        elif self._number == "convection fan1 level":
            self._stove.set_convection_fan1_level(int_value)
        elif self._number == "convection fan1 area":
            self._stove.set_convection_fan1_area(int_value)
        elif self._number == "convection fan2 level":
            self._stove.set_convection_fan2_level(int_value)
        elif self._number == "convection fan2 area":
            self._stove.set_convection_fan2_area(int_value)

        self.schedule_update_ha_state()
