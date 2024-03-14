"""Constants for the Home Assistant Wine Cellar integration."""
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

DOMAIN = "wine_cellar"

SCHEMA_SERVICE_GET_INVENTORY = {}
SCHEMA_SERVICE_REFRESH_INVENTORY = {}

SERVICE_GET_INVENTORY = "get_inventory"
SERVICE_REFRESH_INVENTORY = "refresh_inventory"
