# Wine Cellar

<h2 align="center">
  <a href="https://www.cellartracker.com/"><img src="./img/ct_logo.png" alt="Cellar Tracker logo" width="200"></a>
  <br>
  <i>Home Assistant wine inventory custom integration for cellartracker.com</i>
  <br>
</h2>

The `wine-cellar` implementation allows you to integrate your [Cellar Tracker](https://www.cellartracker.com/) data into Home Assistant.

## Features

- Sensor entity (per account) provides total bottle count.
- Service provides detailed inventory.
- Services provide summaries of inventory.
- Service immediately refresh inventory from Cellar Tracker.

## Disclaimer
This is an unofficial integration of Cellar Tracker for Home Assistant. The developer and the contributors are not, in any way, affiliated with CellarTracker! LLC.

"CellarTracker!" is a trademark of CellarTracker! LLC

## Requirements
- Cellar Tracker account - https://cellartracker.com
- Flex Table Card - Available in HACS or https://github.com/custom-cards/flex-table-card/

## Installation
1. Install manually by copying the `custom_components/wine_cellar` folder into `<config_dir>/custom_components`.
2. Restart Home Assistant.
3. In the Home Assistant UI, navigate to `Settings` then `Devices & services`. In the `Integrations` tab, click on the `ADD INTEGRATION` button at the bottom right and select `Wine Cellar`. Fill out the options and save.
   - Username - Your cellartracker.com Member Name.
   - Password - Your cellartracker.com password.
## Usage

A single sensor entity is provided for each linked CellarTracker account. This could be useful for a quick view of your total bottle count as well as a launch point to more detailed information, as shown here:

<img src="/img/WineSensorEntity.png" alt="Wine Sensor Button" width="25%">

This Tile Card provides the total bottle count, a link to a view with more information called `wine-inventory`, and an `icon_tap_action` to immediately refresh Home Assistant from the CellarTracker database.

```
- type: tile
  entity: sensor.membername_wine_inventory
  name: Wine Inventory
  tap_action:
    action: navigate
    navigation_path: wine-inventory
  icon_tap_action:
    action: call-service
    service: wine_cellar.refresh_inventory
    target:
      entity_id: sensor.membername_wine_inventory
```

More detailed views of the inventory are best presented with the [flex-table-card](https://github.com/custom-cards/flex-table-card). The `flex-table-card` shows data in a tabular form, which works well for a wine database.

## Contribute
Feel free to contribute by opening a PR or issue on this project.
