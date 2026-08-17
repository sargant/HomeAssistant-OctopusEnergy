from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity import DeviceInfo

from ..const import (
  DOMAIN,
)

class OctopusEnergyGasSensor:
  _unrecorded_attributes = frozenset({"data_last_retrieved"})
  _attr_has_entity_name = True

  def __init__(self, hass: HomeAssistant, meter, point, entity_domain = "sensor"):
    """Init sensor"""
    self._point = point
    self._meter = meter
    
    self._mprn = point["mprn"]
    self._serial_number = meter["serial_number"]
    self._is_smart_meter = meter["is_smart_meter"]

    self._attributes = {
      "mprn": self._mprn,
      "serial_number": self._serial_number
    }

    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"gas_{self._serial_number}_{self._mprn}")},
      name=f"Octopus Energy Gas ({self._serial_number}/{self._mprn})",
      connections=set(),
      manufacturer=self._meter["manufacturer"],
      model=self._meter["model"],
      sw_version=self._meter["firmware"]
    )