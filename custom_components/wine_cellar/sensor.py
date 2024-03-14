"""The Home Assistant Wine Cellar integration."""
import logging
from typing import Callable

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.util import slugify
from homeassistant.helpers import entity_platform, service
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SCHEMA_SERVICE_GET_INVENTORY,
    SCHEMA_SERVICE_REFRESH_INVENTORY,
    SERVICE_GET_INVENTORY,
    SERVICE_REFRESH_INVENTORY,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: dict,
    async_add_entities: Callable,
):
    """Set up the Home Assistant Wine Cellar sensors."""
    entities = _create_entities(hass, entry)
    async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()
    _LOGGER.debug(f"platform_name: {platform.platform_name}")

    # This will call Entity._get_inventory
    platform.async_register_entity_service(
        SERVICE_GET_INVENTORY,
        SCHEMA_SERVICE_GET_INVENTORY,
        "_get_inventory",
        supports_response=SupportsResponse.ONLY,
    )

    # This will call Entity._refresh_inventory
    platform.async_register_entity_service(
        SERVICE_REFRESH_INVENTORY,
        SCHEMA_SERVICE_REFRESH_INVENTORY,
        "_refresh_inventory",
    )


def _create_entities(hass: HomeAssistant, entry: dict):
    entities = []

    username = entry.data[CONF_USERNAME]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities.append(WineInventorySensor(entry, username, coordinator))

    return entities


class WineInventorySensor(CoordinatorEntity, SensorEntity):
    """Represent a sensor for the inventory."""

    def __init__(self, entry, username, coordinator):
        """Set up a new HA Cellar Tracker inventory sensor."""
        self._entry = entry
        self._username = username
        self._entity_type = "sensor"
        super().__init__(coordinator)

    @property
    def icon(self) -> str:
        """Return icon."""
        return "mdi:bottle-wine"

    @property
    def name(self) -> str:
        """Return the name of this sensor including the user's name."""
        return f"{self._username} Wine Inventory"

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return slugify(f"{self._entity_type}_{self._username}_wine_inventory")

    @property
    def native_unit_of_measurement(self) -> str:
        """The unit of measurement that the sensor's value is expressed in."""
        return "bottles"

    # @property
    # def extra_state_attributes(self):
    #     attributes = { "inventory": "None" }
    #     _LOGGER.debug("extra_state_attributes")
    #     if self.coordinator.data is not None:
    #         attributes["inventory"] = self._inventory_list()
    #     return attributes

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        _LOGGER.debug("_handle_coordinator_update")
        self._attr_native_value = len(self.coordinator.data)
        return super()._handle_coordinator_update()

    def _inventory_list(self) -> list[dict]:
        """Build a list of dict objects for each bottle in inventory."""
        inventory = []
        for bottle in self.coordinator.data:
            wine = {}
            wine["Barcode"] = bottle["Barcode"]
            wine["Vintage"] = bottle["Vintage"]
            wine["Wine"] = bottle["Wine"]
            wine["Price"] = bottle["Price"]
            wine["StoreName"] = bottle["StoreName"]
            wine["Category"] = bottle["Category"]
            wine["Color"] = bottle["Color"]
            wine["BeginConsume"] = bottle["BeginConsume"]
            wine["EndConsume"] = bottle["EndConsume"]
            wine["Bin"] = bottle["Bin"]
            inventory.append(wine)
        return inventory

    async def _get_inventory(self):
        _LOGGER.debug("_get_inventory")

       # Update the data
        await self.coordinator.async_request_refresh()
        return { "inventory": self._inventory_list() }
        
    async def _refresh_inventory(self):
        _LOGGER.debug("_refresh_inventory")

       # Update the data
        await self.coordinator.async_request_refresh()