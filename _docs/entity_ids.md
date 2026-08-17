# Entity IDs and names

The integration does not set entity IDs. Home Assistant creates them from its configured entity ID format, while the integration continues to provide a stable `unique_id` for every entity.

Entities attached to a device use Home Assistant's device/entity naming model:

* The device name identifies the meter, account or hardware. Electricity meter device names include the MPAN and meter serial number, for example `Electricity Meter (1234567890123/ABC123)`. Gas meter device names use the equivalent MPRN and serial number.
* The entity name identifies only the data point, for example `Current Rate` or `Previous Accumulative Consumption`.

With a device-and-entity ID format, Home Assistant can therefore create an ID such as `sensor.electricity_meter_1234567890123_abc123_current_rate`. The exact ID can differ when your Home Assistant entity ID settings include an area or use a different combination of name parts.

## Existing installations

Existing registered entity IDs are not changed during an upgrade. Automations, dashboards and history continue to use the same IDs unless you explicitly rename or recreate them.

The entity IDs shown elsewhere in this documentation are legacy examples. Use the entity picker or the entity's settings page to find the ID generated for your installation.

## Recreate entity IDs

Home Assistant's [**Recreate entity IDs** action](https://www.home-assistant.io/docs/configuration/customizing-devices/#changing-the-entity-id) rebuilds IDs from the current area, device and entity names, according to your configured entity ID format. This can be useful after giving a meter device a shorter, meaningful name.

Before recreating IDs, make a backup and note that renamed IDs may need updating in automations, scripts, dashboards and external systems.
