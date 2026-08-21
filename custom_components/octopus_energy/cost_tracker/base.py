from homeassistant.helpers.device import async_entity_id_to_device
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from ..const import DOMAIN


class BaseCostTracker:
  def __init__(self, hass, source_entity_id: str, tracker_name: str):
    self.device_entry = async_entity_id_to_device(
      hass,
      source_entity_id,
    )

    self._attr_has_entity_name = True
    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"cost-tracker-{tracker_name}")},
      name=f"Octopus Energy Cost Tracker ({tracker_name})",
      connections=set(),
      entry_type=DeviceEntryType.SERVICE,
    )
