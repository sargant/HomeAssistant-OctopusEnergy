from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .base import OctopusEnergyBaseDataLastRetrieved
from ..const import DOMAIN


class OctopusEnergyAccountDataLastRetrieved(OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the account data was last retrieved."""

  def __init__(self, hass, coordinator, account_id):
    """Init sensor."""
    self._account_id = account_id
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)
    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"account-{account_id}")},
      name=f"Octopus Energy Account ({account_id})",
      connections=set(),
      entry_type=DeviceEntryType.SERVICE,
    )

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_account_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Data Last Retrieved"