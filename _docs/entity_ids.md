# Entity IDs and names

Home Assistant generates entity IDs for Octopus Energy entities using your configured entity naming scheme. The integration keeps stable `unique_id` values for registry identity, while device names carry the identity needed to distinguish meters, accounts and supported Octopus devices. Entity names then describe only the entity-specific data point or control.

For example:

| | Value |
|-|-|
| Device name | `Octopus Energy Electricity (A1B2C3/1234567890123)` |
| Entity name | `Current Rate` |
| Entity ID | `sensor.octopus_energy_electricity_a1b2c3_1234567890123_current_rate` |

The same pattern is used for other entity families. Where the historical entity ID included identifying information such as an account ID, Intelligent device ID, heat pump ID, sensor code, or Cost Tracker name, that information is retained in the default device name rather than repeated in every child entity name.

Existing installations retain their registered entity IDs because the integration's unique IDs have not changed. Home Assistant generates a new entity ID only for a new entity, or when you explicitly use Home Assistant's `Recreate entity IDs` action.

With the `Device Entity` naming scheme, new and recreated entity IDs combine the device name with the entity-specific human-readable name. These IDs may differ from the historical IDs documented elsewhere where the old display name and entity ID used different wording or word order. Renaming a device before using `Recreate entity IDs` also allows the generated IDs to follow your own device naming.
