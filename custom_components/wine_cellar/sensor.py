"""The Home Assistant Wine Cellar integration."""
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

    @property
    def extra_state_attributes(self):
        attributes = { "summary": "None" }
        _LOGGER.debug("extra_state_attributes")
        if self.coordinator.data is not None:
            attributes = self._inventory_summary()
        return attributes

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        _LOGGER.debug("_handle_coordinator_update")
        self._attr_native_value = len(self.coordinator.data)
        return super()._handle_coordinator_update()

    def _inventory_summary(self) -> dict:
        """Build a list of dict objects for each bottle in inventory."""
        data = {}
        df = pd.DataFrame(self.coordinator.data)
        df[["Price","Valuation"]] = df[["Price","Valuation"]].apply(pd.to_numeric)

        groups = ['Varietal', 'Country', 'Vintage', 'Producer', 'Type', 'Location']

        for group in groups:
            group_data = df.groupby(group).agg({'iWine':'count','Valuation':['sum','mean']})
            group_data.columns = group_data.columns.droplevel(0)
            group_data["%"] = 1
            group_data["%"] = (group_data['count']/group_data['count'].sum() ) * 100
            group_data.columns = ["count", "value_total", "value_avg", "%"]
            data[group] = {}
            for row, item in group_data.iterrows():
                if row == "1001":
                    row = "NV"
                data[group][row] = item.to_dict()
                data[group][row]["sub_type"] = row



        data["total_bottles"] = len(df)
        data["total_value"] = df['Valuation'].sum()
        data["average_value"] = df['Valuation'].mean()
        return data

    async def _get_inventory(self):
        _LOGGER.debug("_get_inventory")

       # Update the data
        await self.coordinator.async_request_refresh()
        return { "inventory": self._inventory_list() }
        
    async def _refresh_inventory(self):
        _LOGGER.debug("_refresh_inventory")

       # Update the data
        await self.coordinator.async_request_refresh()