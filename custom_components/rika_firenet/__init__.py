import logging
import requests.exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (CONF_DEFAULT_TEMPERATURE, CONF_PASSWORD,
                    CONF_USERNAME, DOMAIN, PLATFORMS, STARTUP_MESSAGE)
from .core import RikaFirenetCoordinator
from .exceptions import (
    RikaAuthenticationError,
    RikaConnectionError,
    RikaTimeoutError,
    RikaApiError,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    _LOGGER.info('setup_platform()')
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info('async_setup_entry():' + str(entry.entry_id))

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    default_temperature = int(entry.options.get(CONF_DEFAULT_TEMPERATURE, 21))

    coordinator = RikaFirenetCoordinator(hass, username, password, default_temperature)

    try:
        await hass.async_add_executor_job(coordinator.setup)
    except RikaAuthenticationError as exception:
        _LOGGER.error("Authentication failed: %s", exception)
        return False
    except RikaTimeoutError as exception:
        _LOGGER.error("Connection timeout: %s", exception)
        raise ConfigEntryNotReady from exception
    except (RikaConnectionError, RikaApiError) as exception:
        _LOGGER.error("Failed to setup Rika Firenet: %s", exception)
        raise ConfigEntryNotReady from exception
    except KeyError as exception:
        _LOGGER.error("Invalid response from Rika Firenet: %s", exception)
        raise ConfigEntryNotReady from exception

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    coordinator.platforms = [p for p in PLATFORMS if entry.options.get(p, True)]
    await hass.config_entries.async_forward_entry_setups(entry, coordinator.platforms)

    entry.add_update_listener(async_reload_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    unloaded = await hass.config_entries.async_unload_platforms(entry, coordinator.platforms)

    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
