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
    SCHEMA_SERVICE_REFRESH_INVENTORY,
    SERVICE_GET_COUNTRIES,
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
        _LOGGER.debug("extra_state_attributes")
        if self.coordinator.data is not None:
            attributes["summary"] = self._inventory_summary()
        return attributes

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        _LOGGER.debug("_handle_coordinator_update")
        self._attr_native_value = len(self.coordinator.data)
        return super()._handle_coordinator_update()

    def _inventory_summary(self) -> list[dict]:
        """Build a list of dict objects for summary of inventory."""
        summary = []
        data = {}
        df = pd.DataFrame(self.coordinator.data)
        df[["Price","Valuation"]] = df[["Price","Valuation"]].apply(pd.to_numeric).round(0)
        
        data["total_bottles"] = len(df)
        data["total_value"] = "$" + str(int(df['Valuation'].sum().round(0)))
        data["average_value"] = "$" + str(int(df['Valuation'].mean().round(0)))

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

    async def _get_inventory(self):
        _LOGGER.debug("_get_inventory")

       # Update the data
        await self.coordinator.async_request_refresh()
        return { "inventory": self._inventory_list() }

    def _inventory_country_summary(self) -> list[dict]:
        """Build a list of dict objects for summary of inventory by country."""
        summary = []
        df = pd.DataFrame(self.coordinator.data)
        df[["Price","Valuation"]] = df[["Price","Valuation"]].apply(pd.to_numeric).round(0)
        
        group = "Country"
        group_data = df.groupby(group).agg({'iWine':'count','Valuation':['sum','mean']})
        group_data.columns = group_data.columns.droplevel(0)
        group_data["mean"] = group_data["mean"].round(0)
        group_data["%"] = 1
        group_data["%"] = ((group_data['count']/group_data['count'].sum() ) * 100).round(0)
        group_data.columns = ["count", "value_total", "value_avg", "%"]
        data = {}
        for row, item in group_data.iterrows():
          data[row] = item.to_dict()

        keysList = list(data.keys())
        valuesList = list(data.values())
        for index, element in enumerate(keysList):
            the_dict = {'Country': element}
            for key in valuesList[index]:
                the_dict[key] = valuesList[index][key]
            summary.append(the_dict)

        return summary

    async def _get_countries(self):
        _LOGGER.debug("get_countries")

        return { "countries": self._inventory_country_summary() }

    async def _refresh_inventory(self):
        _LOGGER.debug("_refresh_inventory")

       # Update the data
        await self.coordinator.async_request_refresh()