# Entity IDs and names

As of v20.0.0, the integration does not set entity IDs. Home Assistant creates them from its configured entity ID format, while the integration continues to provide a stable `unique_id` for every entity.

Entities attached to a device use Home Assistant's device/entity naming model:

* The device name identifies the meter, account or hardware. Electricity meter device names include the meter serial number and MPAN, for example `Octopus Energy Electricity (ABC123/1234567890123)`. Gas meter device names use the equivalent serial number and MPRN.
* The entity name retains its existing descriptive text but no longer repeats the meter serial number and MPAN/MPRN, for example `Current Rate Electricity` or `Previous Accumulative Consumption Gas`.

With a device-and-entity ID format, Home Assistant can therefore create an ID such as `sensor.octopus_energy_electricity_abc123_1234567890123_current_rate_electricity`. The exact ID can differ when your Home Assistant entity ID settings include an area or use a different combination of name parts.

## Existing installations

Existing registered entity IDs are not changed during an upgrade. Automations, dashboards and history continue to use the same IDs unless you explicitly rename or recreate them.

The entity IDs shown elsewhere in this documentation assume your entity naming scheme is "`Device` `Entity`". Use the entity picker or the entity's settings page to find the ID generated for your installation.

## Recreate entity IDs

Home Assistant's [**Recreate entity IDs** action](https://www.home-assistant.io/docs/configuration/customizing-devices/#changing-the-entity-id) rebuilds IDs from the current area, device and entity names, according to your configured entity ID format. This can be useful after giving a meter device a shorter, meaningful name.

Before recreating IDs, make a backup and note that renamed IDs may need updating in automations, scripts, dashboards and external systems.
