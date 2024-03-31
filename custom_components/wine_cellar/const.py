"""Constants for the Home Assistant Wine Cellar integration."""
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

DOMAIN = "wine_cellar"

SCHEMA_SERVICE_GET_COUNTRIES = {}
SCHEMA_SERVICE_GET_INVENTORY = {}
SCHEMA_SERVICE_GET_LOCATIONS = {}
SCHEMA_SERVICE_GET_PRODUCERS = {}
SCHEMA_SERVICE_GET_TYPES = {}
SCHEMA_SERVICE_GET_VARIETALS = {}
SCHEMA_SERVICE_GET_VINTAGES = {}
SCHEMA_SERVICE_REFRESH_INVENTORY = {}

SERVICE_GET_COUNTRIES = "get_countries"
SERVICE_GET_INVENTORY = "get_inventory"
SERVICE_GET_LOCATIONS = "get_locations"
SERVICE_GET_PRODUCERS = "get_producers"
SERVICE_GET_TYPES = "get_types"
SERVICE_GET_VARIETALS = "get_varietals"
SERVICE_GET_VINTAGES = "get_vintages"
SERVICE_REFRESH_INVENTORY = "refresh_inventory"
