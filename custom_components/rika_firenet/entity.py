import logging
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, DEFAULT_NAME, VERSION
from .core import RikaFirenetStove, RikaFirenetCoordinator

_LOGGER = logging.getLogger(__name__)


class RikaFirenetEntity(CoordinatorEntity):
    def __init__(self, config_entry, stove: RikaFirenetStove, coordinator: RikaFirenetCoordinator, suffix=None):
        super().__init__(coordinator)

        self._config_entry = config_entry
        self._stove = stove

        if suffix is not None:
            self._name = f"{stove.get_name()} {suffix}"
            self._unique_id = f"{suffix} {stove.get_name()}"
        else:
            self._name = stove.get_name()
            self._unique_id = stove.get_id()

        _LOGGER.info('RikaFirenetEntity creation with name: ' + self._name + ' unique_id: ' + self._unique_id)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": NAME,
            "model": VERSION,
            "manufacturer": DEFAULT_NAME,
        }
