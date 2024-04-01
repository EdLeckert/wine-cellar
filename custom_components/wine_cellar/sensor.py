"""The Home Assistant Wine Cellar integration."""
import enum
import pandas as pd
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
    SCHEMA_SERVICE_GET_COUNTRIES,
    SCHEMA_SERVICE_GET_INVENTORY,
    SCHEMA_SERVICE_GET_LOCATIONS,
    SCHEMA_SERVICE_GET_PRODUCERS,
    SCHEMA_SERVICE_GET_TYPES,
    SCHEMA_SERVICE_GET_VARIETALS,
    SCHEMA_SERVICE_GET_VINTAGES,
    SCHEMA_SERVICE_REFRESH_INVENTORY,
    SERVICE_GET_COUNTRIES,
    SERVICE_GET_INVENTORY,
    SERVICE_GET_LOCATIONS,
    SERVICE_GET_PRODUCERS,
    SERVICE_GET_TYPES,
    SERVICE_GET_VARIETALS,
    SERVICE_GET_VINTAGES,
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

    # This will call Entity._get_countries
    platform.async_register_entity_service(
        SERVICE_GET_COUNTRIES,
        SCHEMA_SERVICE_GET_COUNTRIES,
        "_get_countries",
        supports_response=SupportsResponse.ONLY,
    )

    # This will call Entity._get_inventory
    platform.async_register_entity_service(
        SERVICE_GET_INVENTORY,
        SCHEMA_SERVICE_GET_INVENTORY,
        "_get_inventory",
        supports_response=SupportsResponse.ONLY,
    )

    # This will call Entity._get_locations
    platform.async_register_entity_service(
        SERVICE_GET_LOCATIONS,
        SCHEMA_SERVICE_GET_LOCATIONS,
        "_get_locations",
        supports_response=SupportsResponse.ONLY,
    )

    # This will call Entity._get_producers
    platform.async_register_entity_service(
        SERVICE_GET_PRODUCERS,
        SCHEMA_SERVICE_GET_PRODUCERS,
        "_get_producers",
        supports_response=SupportsResponse.ONLY,
    )

    # This will call Entity._get_types
    platform.async_register_entity_service(
        SERVICE_GET_TYPES,
        SCHEMA_SERVICE_GET_TYPES,
        "_get_types",
        supports_response=SupportsResponse.ONLY,
    )

    # This will call Entity._get_varietals
    platform.async_register_entity_service(
        SERVICE_GET_VARIETALS,
        SCHEMA_SERVICE_GET_VARIETALS,
        "_get_varietals",
        supports_response=SupportsResponse.ONLY,
    )

    # This will call Entity._get_vintages
    platform.async_register_entity_service(
        SERVICE_GET_VINTAGES,
        SCHEMA_SERVICE_GET_VINTAGES,
        "_get_vintages",
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

    @property
    def extra_state_attributes(self):
        attributes = { "summary": "None" }
        if self.coordinator.data is not None:
            attributes["summary"] = self._inventory_summary()
        return attributes

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        self._attr_native_value = len(self.coordinator.data)
        return super()._handle_coordinator_update()

    def _inventory_summary(self) -> list[dict]:
        """Build a list of dict objects for summary of inventory."""
        summary = []
        data = {}
        df = pd.DataFrame(self.coordinator.data)
        df[["Price","Valuation"]] = df[["Price","Valuation"]].apply(pd.to_numeric).round(0)
        
        data["total_bottles"] = len(df)
        data["total_value"] = int(df['Valuation'].sum().round(0))
        data["average_value"] = int(df['Valuation'].mean().round(0))

        summary.append(data)
        return summary

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

    def _inventory_group_summary(self, group) -> list[dict]:
        """Build a list of dict objects for summary of inventory by country."""
        summary = []
        df = pd.DataFrame(self.coordinator.data)
        df[["Price","Valuation"]] = df[["Price","Valuation"]].apply(pd.to_numeric).round(0)
        
        group_data = df.groupby(group).agg({'iWine':'count','Valuation':['sum','mean']})
        group_data.columns = group_data.columns.droplevel(0)
        group_data["mean"] = group_data["mean"].round(0)
        group_data["percent"] = 1
        group_data["percent"] = ((group_data['count']/group_data['count'].sum() ) * 100).round(0)
        group_data.columns = ["count", "value_total", "value_avg", "percent"]
        data = {}
        for row, item in group_data.iterrows():
          data[row] = item.to_dict()

        keysList = list(data.keys())
        valuesList = list(data.values())
        for index, element in enumerate(keysList):
            the_dict = {group: element}
            for key in valuesList[index]:
                the_dict[key] = valuesList[index][key]
            summary.append(the_dict)

        return summary

    async def _get_countries(self):
        return { "countries": self._inventory_group_summary("Country") }

    async def _get_inventory(self):
       # Update the data
        return { "inventory": self._inventory_list() }

    async def _get_locations(self):
        return { "locations": self._inventory_group_summary("Location") }

    async def _get_producers(self):
        return { "producers": self._inventory_group_summary("Producer") }

    async def _get_types(self):
        return { "types": self._inventory_group_summary("Type") }

    async def _get_varietals(self):
        return { "varietals": self._inventory_group_summary("Varietal") }

    async def _get_vintages(self):
        return { "vintages": self._inventory_group_summary("Vintage") }

    async def _refresh_inventory(self):

       # Update the data
        await self.coordinator.async_request_refresh()
