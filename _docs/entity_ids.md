# Entity IDs and names

Home Assistant generates entity IDs for electricity and gas meter entities from the device and entity names. With Home Assistant's `Device Entity` naming scheme, the device supplies the meter-specific prefix and the entity supplies the remaining suffix.

For example:

| | Value |
|-|-|
| Device name | `Octopus Energy Electricity (A1B2C3/1234567890123)` |
| Entity name | `Current Rate` |
| Entity ID | `sensor.octopus_energy_electricity_a1b2c3_1234567890123_current_rate` |

The entity IDs documented on the electricity and gas pages use this format. Export electricity entities include `Export` at the start of the entity name so their generated entity IDs retain the existing `_export_` placement.

Existing installations retain their registered entity IDs because the integration's unique IDs have not changed. Home Assistant generates a new entity ID only for a new entity, or when you explicitly use Home Assistant's `Recreate entity IDs` action.

If you use a different entity naming scheme, Home Assistant may generate different entity IDs.
