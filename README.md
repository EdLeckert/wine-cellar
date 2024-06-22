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

### Sensor Entity
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

### Inventory List Service
More detailed views of the inventory are best presented with the [flex-table-card](https://github.com/custom-cards/flex-table-card). The `flex-table-card` shows data in a tabular form, which works well for a wine database.

Consider this list of wines as shown in a `flex-table-card`:

<img src="/img/WineInventoryList.png" alt="Wine Inventory List" width="100%">

The card definition for the above view demonstrates some advanced features of the card which can be used to mimic CellarTracker's display of icons. Notice the use of the `service` option to populate the table using the `wine_cellar.get_inventory` service.

```
- type: custom:flex-table-card
  service: wine_cellar.get_inventory
  entities:
    include: sensor.membername_wine_inventory
  clickable: true
  sort_by:
    - ConsumeBy
    - Vintage
  columns:
    - name: ''
      data: inventory
      align: center
      modify: |-
        function getColor(wineColor) {
          let color="red";
          switch(wineColor) {
              case "Red":
                color="DarkRed"
                break;
              case "White":
                color="Khaki"
                break;
              case "Rosé":
                color="LightPink"
                break;
              default:
                color="White";
                break;
          }
          return color;
        }  function getIcon(wineType) {
          let icon="mdi:glass-wine";
          switch(wineType) {
              case "Dry":
                icon="mdi:glass-wine"
                break;
              case "Sweet/Dessert":
                icon="mdi:glass-tulip"
                break;
              case "Sparkling":
                icon="mdi:glass-flute"
                break;
              default:
                icon="mdi:glass-wine"
                break;
          }
          return icon;
        } '<ha-icon icon=' + getIcon(x.Category) + ' style=color:' +
        getColor(x.Color) + ';></ha-icon>'
    - name: Barcode
      data: inventory
      modify: x.Barcode
      hidden: true
    - name: Vintage
      data: inventory
      modify: if(parseInt(x.Vintage) == 1001) {"N.V."} else{parseInt(x.Vintage)}
    - name: Wine
      data: inventory
      modify: x.Wine
    - name: ConsumeBy
      data: inventory
      modify: |-
        ((parseInt(x.BeginConsume) || 9999) +
         (parseInt(x.EndConsume) || 9999)) / 2
      hidden: true
    - name: Category
      data: inventory
      modify: x.Category + " " + x.Color
    - name: Consume
      data: inventory
      modify: |-
        let result = 
          x.BeginConsume == "" && x.EndConsume == "" 
          ? "None"
          : x.BeginConsume + "-" + x.EndConsume;
          parseInt(x.BeginConsume) > new Date().getFullYear()
            ? '<div class="too-early">' + result + '</div>'
            : parseInt(x.EndConsume) < new Date().getFullYear()
              ?'<div class="too-late">' + result + '</div>'
              : result
    - name: Bin
      data: inventory
      modify: x.Bin
    - name: Price
      data: inventory
      modify: >-
        if (x.Price == 0 ) {"N/A"} else {"$" +
        parseFloat(x.Price).toFixed(0)}
    - name: Store
      data: inventory
      modify: x.StoreName
  css:
    tr:has(> td div.too-early): color:dimgray !important;
    tr:has(> td div.too-late): color:red !important;
```

### Inventory Summary Services

A group of services is available to summarize the inventory by various fields. They are:

- wine_cellar.get_countries
- wine_cellar.get_locations
- wine_cellar.get_producers
- wine_cellar.get_types
- wine_cellar.get_varietals
- wine_cellar.get_vintages

Some examples of their use:

<img src="/img/WineInventorySummary.png" alt="Wine Inventory Summaries" width="100%">

The card for the summary by Country:

```
type: custom:flex-table-card
title: Bottles per Country
service: wine_cellar.get_countries
entities:
  include: sensor.membername_wine_inventory
sort_by: Country-
columns:
  - name: Country
    data: countries
    modify: x.Country
  - name: Percentage
    data: countries
    modify: x.percent
    align: right
  - name: Total Cost
    data: countries
    modify: x.value_total
    align: right
    prefix: $
  - name: Average Price
    data: countries
    modify: x.value_avg
    align: right
    prefix: $
  - name: Bottles
    data: countries
    modify: x.count
    align: right
```

## Contribute
Feel free to contribute by opening a PR or issue on this project.
