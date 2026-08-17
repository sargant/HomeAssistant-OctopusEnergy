import ast
from pathlib import Path

from homeassistant.helpers.entity import Entity

from custom_components.octopus_energy.electricity.base import OctopusEnergyElectricitySensor
from custom_components.octopus_energy.gas.base import OctopusEnergyGasSensor
from custom_components.octopus_energy.heat_pump.base import BaseOctopusEnergyHeatPumpSensor
from custom_components.octopus_energy.intelligent.base import OctopusEnergyIntelligentSensor
from custom_components.octopus_energy.octoplus.base import OctopusEnergyOctoplusSensor


class ElectricityEntity(OctopusEnergyElectricitySensor, Entity):
  @property
  def unique_id(self):
    return "electricity-test"


class GasEntity(OctopusEnergyGasSensor, Entity):
  @property
  def unique_id(self):
    return "gas-test"


def test_meter_entities_defer_entity_id_generation_to_home_assistant():
  meter = {
    "serial_number": "serial",
    "is_export": False,
    "is_smart_meter": True,
    "manufacturer": "manufacturer",
    "model": "model",
    "firmware": "firmware",
  }

  electricity = ElectricityEntity(None, meter, {"mpan": "mpan"})
  gas = GasEntity(None, meter, {"mprn": "mprn"})

  assert electricity.entity_id is None
  assert electricity.has_entity_name is True
  assert electricity.device_info["name"] == "Octopus Energy Electricity Meter (serial/mpan)"

  assert gas.entity_id is None
  assert gas.has_entity_name is True
  assert gas.device_info["name"] == "Octopus Energy Gas Meter (serial/mprn)"


def test_integration_does_not_generate_entity_ids():
  integration = Path(__file__).parents[2] / "custom_components" / "octopus_energy"

  for path in integration.rglob("*.py"):
    assert "generate_entity_id" not in path.read_text()


def test_entity_names_do_not_include_meter_identifiers():
  integration = Path(__file__).parents[2] / "custom_components" / "octopus_energy"

  for path in integration.rglob("*.py"):
    source = path.read_text()
    for node in ast.walk(ast.parse(source)):
      if isinstance(node, ast.FunctionDef) and node.name == "name":
        name_source = ast.get_source_segment(source, node)
        assert "_serial_number" not in name_source
        assert "_mpan" not in name_source
        assert "_mprn" not in name_source


def test_device_entities_use_home_assistant_entity_naming():
  device_entity_bases = (
    OctopusEnergyElectricitySensor,
    OctopusEnergyGasSensor,
    BaseOctopusEnergyHeatPumpSensor,
    OctopusEnergyIntelligentSensor,
    OctopusEnergyOctoplusSensor,
  )

  assert all(entity_base._attr_has_entity_name for entity_base in device_entity_bases)
