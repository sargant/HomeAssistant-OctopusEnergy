from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from ..const import DOMAIN


class OctopusEnergyWheelOfFortuneSensor:
  """Base entity for Wheel of Fortune sensors."""

  def __init__(self, account_id: str):
    self._attr_has_entity_name = True
    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"wheel-of-fortune-{account_id}")},
      name=f"Wheel Of Fortune ({account_id})",
      connections=set(),
      entry_type=DeviceEntryType.SERVICE,
    )
