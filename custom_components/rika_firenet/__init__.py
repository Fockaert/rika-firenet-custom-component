import asyncio
import logging
from datetime import timedelta

import requests.exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval

from .const import (CONF_DEFAULT_TEMPERATURE, CONF_HOST, CONF_PASSWORD,
					CONF_USERNAME, DOMAIN, PLATFORMS, STARTUP_MESSAGE)
from .core import RikaFirenetConnector

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)
SCAN_INTERVAL = timedelta(seconds=15)


async def async_setup(hass: HomeAssistant, config: dict):
    _LOGGER.info('setup_platform()')
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info('async_setup_entry():' + str(entry.entry_id))

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    host = entry.data.get(CONF_HOST)
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    default_temperature = int(entry.data.get(CONF_DEFAULT_TEMPERATURE))

    connector = RikaFirenetConnector(hass, host, username, password, default_temperature)

    try:
        await hass.async_add_executor_job(connector.setup)
    except KeyError:
        _LOGGER.error("Failed to login to firenet")
        return False
    except RuntimeError as exc:
        _LOGGER.error("Failed to setup rika firenet: %s", exc)
        return ConfigEntryNotReady
    except requests.exceptions.Timeout as ex:
        raise ConfigEntryNotReady from ex
    except requests.exceptions.HTTPError as ex:
        if ex.response.status_code > 400 and ex.response.status_code < 500:
            _LOGGER.error("Failed to login to rika firenet: %s", ex)
            return False
        raise ConfigEntryNotReady from ex

    # Do first update
    await hass.async_add_executor_job(connector.update)

    # Poll for updates in the background
    async_track_time_interval(
        hass,
        lambda now: connector.update(),
        SCAN_INTERVAL,
    )

    hass.data[DOMAIN][entry.entry_id] = connector

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            connector.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.add_update_listener(async_reload_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    connector = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in connector.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
