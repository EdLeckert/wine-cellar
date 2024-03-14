"""The Home Assistant Wine Cellar integration."""
from __future__ import annotations

from datetime import timedelta
import logging
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.exceptions import ConfigEntryAuthFailed
from cellartracker.errors import AuthenticationError, CannotConnect
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.entity_platform import async_get_platforms

from cellartracker import cellartracker
from cellartracker.errors import AuthenticationError, CannotConnect

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Assistant Wine Cellar from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    try:
        controller = cellartracker.CellarTracker(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])

        # Request some data to validate username/password.
        await hass.async_add_executor_job(controller.get_food_tag)

    except (AuthenticationError, CannotConnect) as exc:
        _LOGGER.error(f"Unable to connect to Cellar Tracker controller: {str(exc)}")
        raise ConfigEntryNotReady

    coordinator = MyCoordinator(hass, controller)

    hass.data[DOMAIN][entry.entry_id] = {
            "coordinator": coordinator,
            "controller": controller,
        }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    return True


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, controller):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="CellarTracker",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=3600),
        )
        self._hass = hass
        self._controller = controller

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self._hass.async_add_executor_job(self._controller.get_inventory)

        except AuthenticationError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except CannotConnect as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
