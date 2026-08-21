from datetime import timedelta
import logging
from types import MappingProxyType
from unittest.mock import Mock

import pytest
import pytest_asyncio

from homeassistant.config_entries import ConfigEntries, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.entity_platform import EntityPlatform

from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice
from custom_components.octopus_energy.const import (
  CONFIG_COST_TRACKER_NAME,
  CONFIG_COST_TRACKER_TARGET_ENTITY_ID,
  DOMAIN,
  INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES,
)
from custom_components.octopus_energy.cost_tracker.cost_tracker import (
  OctopusEnergyCostTrackerSensor,
)
from custom_components.octopus_energy.diagnostics_entities.account_data_last_retrieved import (
  OctopusEnergyAccountDataLastRetrieved,
)
from custom_components.octopus_energy.diagnostics_entities.electricity_previous_consumption_and_rates_data_last_retrieved import (
  OctopusEnergyElectricityPreviousConsumptionAndRatesDataLastRetrieved,
)
from custom_components.octopus_energy.diagnostics_entities.wheel_of_fortune_data_last_retrieved import (
  OctopusEnergyWheelOfFortuneDataLastRetrieved,
)
from custom_components.octopus_energy.electricity.current_accumulative_consumption import (
  OctopusEnergyCurrentAccumulativeElectricityConsumption,
)
from custom_components.octopus_energy.electricity.current_rate import (
  OctopusEnergyElectricityCurrentRate,
)
from custom_components.octopus_energy.electricity.off_peak import (
  OctopusEnergyElectricityOffPeak,
)
from custom_components.octopus_energy.electricity.previous_accumulative_cost_override import (
  OctopusEnergyPreviousAccumulativeElectricityCostOverride,
)
from custom_components.octopus_energy.gas.current_accumulative_consumption_kwh import (
  OctopusEnergyCurrentAccumulativeGasConsumptionKwh,
)
from custom_components.octopus_energy.gas.current_rate import OctopusEnergyGasCurrentRate
from custom_components.octopus_energy.gas.current_total_consumption_kwh import (
  OctopusEnergyCurrentTotalGasConsumptionKwh,
)
from custom_components.octopus_energy.heat_pump.live_cop import (
  OctopusEnergyHeatPumpLiveCoP,
)
from custom_components.octopus_energy.heat_pump.sensor_temperature import (
  OctopusEnergyHeatPumpSensorTemperature,
)
from custom_components.octopus_energy.home_pro.screen_text import (
  OctopusEnergyHomeProScreenText,
)
from custom_components.octopus_energy.intelligent.current_state import (
  OctopusEnergyIntelligentCurrentState,
)
from custom_components.octopus_energy.octoplus.points import OctopusEnergyOctoplusPoints
from custom_components.octopus_energy.octoplus.power_down_baseline import (
  OctopusEnergyPowerDownBaseline,
)
from custom_components.octopus_energy.wheel_of_fortune.electricity_spins import (
  OctopusEnergyWheelOfFortuneElectricitySpins,
)


pytestmark = pytest.mark.asyncio

ELECTRICITY_SERIAL = "ELECTRICITYSERIAL"
MPAN = "1234567890123"
GAS_SERIAL = "GASSERIAL"
MPRN = "9876543210"
ACCOUNT_ID = "A-TEST"
INTELLIGENT_DEVICE_ID = "DEVICE-123"
HEAT_PUMP_ID = "HP-ABC"
HEAT_PUMP_SERIAL = "HP-SERIAL"
HEAT_PUMP_SENSOR_CODE = "SENSOR-1"


@pytest_asyncio.fixture
async def hass(tmp_path):
  hass = HomeAssistant(str(tmp_path))
  hass.config_entries = ConfigEntries(hass, {})
  await device_registry.async_load(hass)
  await entity_registry.async_load(hass)

  yield hass

  await hass.async_stop(force=True)


def create_config_entry(hass):
  entry = ConfigEntry(
    data={},
    discovery_keys=MappingProxyType({}),
    domain=DOMAIN,
    minor_version=1,
    options={},
    source="user",
    subentries_data=None,
    title="Octopus Energy",
    unique_id=ACCOUNT_ID,
    version=1,
  )
  hass.config_entries._entries[entry.entry_id] = entry
  return entry


def create_platform(hass, entry, domain="sensor"):
  platform = EntityPlatform(
    hass=hass,
    logger=logging.getLogger(__name__),
    domain=domain,
    platform_name=DOMAIN,
    platform=None,
    scan_interval=timedelta(seconds=30),
    entity_namespace=None,
  )
  platform.config_entry = entry
  return platform


def create_coordinator():
  coordinator = Mock()
  coordinator.data = None
  coordinator.last_update_success = True
  coordinator.async_add_listener.return_value = lambda: None
  return coordinator


def electricity_meter(is_export=False):
  return {
    "serial_number": ELECTRICITY_SERIAL,
    "is_export": is_export,
    "is_smart_meter": True,
    "manufacturer": "Test Manufacturer",
    "model": "Test Model",
    "firmware": "1.0",
  }


def gas_meter():
  return {
    "serial_number": GAS_SERIAL,
    "is_smart_meter": True,
    "manufacturer": "Test Manufacturer",
    "model": "Test Model",
    "firmware": "1.0",
  }


def intelligent_device():
  return IntelligentDevice(
    INTELLIGENT_DEVICE_ID,
    "TESLA",
    "Tesla",
    "Model Y",
    75,
    None,
    INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES,
  )


def heat_pump():
  return Mock(
    serialNumber=HEAT_PUMP_SERIAL,
    model="Cosy 6",
    hardwareVersion="1.0",
  )


def heat_pump_sensor():
  return Mock(
    code=HEAT_PUMP_SENSOR_CODE,
    displayName="Living Room",
    type="WIRELESS",
    firmwareVersion="1.0",
  )


def entity_device(hass, entity):
  registry_entry = entity_registry.async_get(hass).async_get(entity.entity_id)
  return device_registry.async_get(hass).async_get(registry_entry.device_id)


async def test_new_electricity_entity_uses_device_entity_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyElectricityCurrentRate(
    hass,
    create_coordinator(),
    electricity_meter(),
    {"mpan": MPAN},
    None,
    ACCOUNT_ID,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_current_rate"
  assert entity.has_entity_name is True
  assert entity.entity_id == f"sensor.octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_current_rate"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Electricity ({ELECTRICITY_SERIAL}/{MPAN})"
  assert device.identifiers == {(DOMAIN, f"electricity_{ELECTRICITY_SERIAL}_{MPAN}")}


async def test_new_gas_entity_uses_device_entity_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyGasCurrentRate(
    hass,
    create_coordinator(),
    gas_meter(),
    {"mprn": MPRN},
    None,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_gas_{GAS_SERIAL}_{MPRN}_current_rate"
  assert entity.has_entity_name is True
  assert entity.entity_id == f"sensor.octopus_energy_gas_{GAS_SERIAL.lower()}_{MPRN}_current_rate"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Gas ({GAS_SERIAL}/{MPRN})"
  assert device.identifiers == {(DOMAIN, f"gas_{GAS_SERIAL}_{MPRN}")}


async def test_existing_registry_entity_id_is_preserved(hass):
  entry = create_config_entry(hass)
  unique_id = f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_current_rate"
  existing = entity_registry.async_get(hass).async_get_or_create(
    "sensor",
    DOMAIN,
    unique_id,
    calculated_object_id=f"octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_current_rate",
    config_entry=entry,
  )
  entity = OctopusEnergyElectricityCurrentRate(
    hass,
    create_coordinator(),
    electricity_meter(),
    {"mpan": MPAN},
    None,
    ACCOUNT_ID,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == unique_id
  assert entity.entity_id == existing.entity_id


async def test_export_variant_preserves_human_name_order(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyElectricityOffPeak(
    hass,
    create_coordinator(),
    electricity_meter(is_export=True),
    {"mpan": MPAN},
  )

  await create_platform(hass, entry, domain="binary_sensor").async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_export_off_peak"
  assert entity.has_entity_name is True
  assert entity.name == "Off Peak Export"
  assert entity.entity_id == f"binary_sensor.octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_off_peak_export"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Electricity ({ELECTRICITY_SERIAL}/{MPAN})"


async def test_meter_diagnostic_uses_preserved_human_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyElectricityPreviousConsumptionAndRatesDataLastRetrieved(
    hass,
    create_coordinator(),
    electricity_meter(),
    {"mpan": MPAN},
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_previous_consumption_rates_data_last_retrieved"
  assert entity.has_entity_name is True
  assert entity.name == "Previous Consumption and Rates Data Last Retrieved"
  assert entity.entity_id == f"sensor.octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_previous_consumption_and_rates_data_last_retrieved"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Electricity ({ELECTRICITY_SERIAL}/{MPAN})"


async def test_meter_entity_names_remove_only_device_context(hass):
  electricity_point = {"mpan": MPAN}
  gas_point = {"mprn": MPRN}

  peak_consumption = OctopusEnergyCurrentAccumulativeElectricityConsumption(
    hass,
    create_coordinator(),
    create_coordinator(),
    create_coordinator(),
    electricity_meter(),
    electricity_point,
    "off_peak",
  )
  tariff_cost = OctopusEnergyPreviousAccumulativeElectricityCostOverride(
    hass,
    ACCOUNT_ID,
    create_coordinator(),
    Mock(),
    electricity_meter(),
    electricity_point,
    {"name": "Agile"},
  )
  gas_consumption = OctopusEnergyCurrentAccumulativeGasConsumptionKwh(
    hass,
    create_coordinator(),
    create_coordinator(),
    create_coordinator(),
    gas_meter(),
    gas_point,
    40,
  )
  gas_total = OctopusEnergyCurrentTotalGasConsumptionKwh(
    hass,
    create_coordinator(),
    gas_meter(),
    gas_point,
    40,
  )

  assert peak_consumption.name == "Off Peak Current Accumulative Consumption"
  assert tariff_cost.name == "Agile Previous Accumulative Cost Override"
  assert gas_consumption.name == "Current Accumulative Consumption"
  assert gas_total.name == "Current Total Consumption (kWh)"


async def test_octoplus_baseline_uses_device_entity_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyPowerDownBaseline(
    hass,
    create_coordinator(),
    create_coordinator(),
    electricity_meter(),
    {"mpan": MPAN},
    False,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_octoplus_power_down_baseline"
  assert entity.has_entity_name is True
  assert entity.name == "Octoplus Power Down Baseline"
  assert entity.entity_id == f"sensor.octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_octoplus_power_down_baseline"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Electricity ({ELECTRICITY_SERIAL}/{MPAN})"


async def test_intelligent_entity_uses_identity_bearing_device_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyIntelligentCurrentState(
    hass,
    create_coordinator(),
    intelligent_device(),
    ACCOUNT_ID,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_{INTELLIGENT_DEVICE_ID}_intelligent_state"
  assert entity.has_entity_name is True
  assert entity.name == "Intelligent State"
  assert entity.entity_id == "sensor.tesla_model_y_electric_vehicle_device_123_intelligent_state"

  device = entity_device(hass, entity)
  assert device.name == f"Tesla Model Y (Electric Vehicle/{INTELLIGENT_DEVICE_ID})"
  assert device.identifiers == {(DOMAIN, INTELLIGENT_DEVICE_ID)}


async def test_existing_intelligent_entity_id_is_preserved(hass):
  entry = create_config_entry(hass)
  unique_id = f"octopus_energy_{INTELLIGENT_DEVICE_ID}_intelligent_state"
  existing = entity_registry.async_get(hass).async_get_or_create(
    "sensor",
    DOMAIN,
    unique_id,
    calculated_object_id="octopus_energy_device_123_intelligent_state",
    config_entry=entry,
  )
  entity = OctopusEnergyIntelligentCurrentState(
    hass,
    create_coordinator(),
    intelligent_device(),
    ACCOUNT_ID,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == unique_id
  assert entity.entity_id == existing.entity_id


async def test_octoplus_points_uses_account_device_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyOctoplusPoints(hass, Mock(), ACCOUNT_ID)

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_{ACCOUNT_ID}_octoplus_points"
  assert entity.has_entity_name is True
  assert entity.name == "Points"
  assert entity.entity_id == "sensor.octoplus_a_test_points"

  device = entity_device(hass, entity)
  assert device.name == f"Octoplus ({ACCOUNT_ID})"
  assert device.identifiers == {(DOMAIN, f"octoplus-{ACCOUNT_ID}")}


async def test_heat_pump_entity_uses_heat_pump_identity_in_device_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyHeatPumpLiveCoP(
    hass,
    create_coordinator(),
    HEAT_PUMP_ID,
    heat_pump(),
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_heat_pump_{HEAT_PUMP_ID}_live_cop"
  assert entity.has_entity_name is True
  assert entity.name == "Live CoP"
  assert entity.entity_id == "sensor.octopus_energy_heat_pump_hp_abc_hp_serial_live_cop"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Heat Pump ({HEAT_PUMP_ID}/{HEAT_PUMP_SERIAL})"
  assert device.identifiers == {(DOMAIN, f"heat_pump_{HEAT_PUMP_SERIAL}")}


async def test_heat_pump_sensor_uses_sensor_identity_in_device_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyHeatPumpSensorTemperature(
    hass,
    create_coordinator(),
    HEAT_PUMP_ID,
    heat_pump(),
    heat_pump_sensor(),
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_heat_pump_{HEAT_PUMP_ID}_{HEAT_PUMP_SENSOR_CODE}_temperature"
  assert entity.has_entity_name is True
  assert entity.name == "Temperature"
  assert entity.entity_id == "sensor.octopus_energy_heat_pump_sensor_living_room_hp_abc_sensor_1_temperature"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Heat Pump Sensor Living Room ({HEAT_PUMP_ID}/{HEAT_PUMP_SENSOR_CODE})"
  assert device.identifiers == {(DOMAIN, f"heat_pump_sensor_{HEAT_PUMP_SERIAL}_{HEAT_PUMP_SENSOR_CODE}")}


async def test_home_pro_screen_uses_service_device_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyHomeProScreenText(hass, ACCOUNT_ID, Mock())

  await create_platform(hass, entry, domain="text").async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_{ACCOUNT_ID}_home_pro_screen"
  assert entity.has_entity_name is True
  assert entity.name == "Screen"
  assert entity.entity_id == "text.octopus_energy_home_pro_a_test_screen"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Home Pro ({ACCOUNT_ID})"
  assert device.identifiers == {(DOMAIN, f"home_pro_{ACCOUNT_ID}")}


async def test_wheel_entities_share_service_device(hass):
  entry = create_config_entry(hass)
  coordinator = create_coordinator()
  spins = OctopusEnergyWheelOfFortuneElectricitySpins(
    hass,
    coordinator,
    Mock(),
    ACCOUNT_ID,
  )
  diagnostic = OctopusEnergyWheelOfFortuneDataLastRetrieved(
    hass,
    coordinator,
    ACCOUNT_ID,
  )

  await create_platform(hass, entry).async_add_entities([spins, diagnostic])

  assert spins.has_entity_name is True
  assert spins.name == "Electricity Spins"
  assert spins.entity_id == "sensor.wheel_of_fortune_a_test_electricity_spins"
  assert diagnostic.has_entity_name is True
  assert diagnostic.name == "Data Last Retrieved"
  assert diagnostic.entity_id == "sensor.wheel_of_fortune_a_test_data_last_retrieved"

  registry = entity_registry.async_get(hass)
  spins_registry_entry = registry.async_get(spins.entity_id)
  diagnostic_registry_entry = registry.async_get(diagnostic.entity_id)
  assert spins_registry_entry.device_id == diagnostic_registry_entry.device_id

  device = device_registry.async_get(hass).async_get(spins_registry_entry.device_id)
  assert device.name == f"Wheel Of Fortune ({ACCOUNT_ID})"
  assert device.identifiers == {(DOMAIN, f"wheel-of-fortune-{ACCOUNT_ID}")}


async def test_cost_tracker_uses_tracker_name_as_device_identity(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyCostTrackerSensor(
    hass,
    create_coordinator(),
    entry,
    {
      CONFIG_COST_TRACKER_NAME: "Kitchen",
      CONFIG_COST_TRACKER_TARGET_ENTITY_ID: "sensor.kitchen_energy",
    },
    None,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == "octopus_energy_cost_tracker_Kitchen"
  assert entity.has_entity_name is True
  assert entity.name == "Daily Cost"
  assert entity.entity_id == "sensor.octopus_energy_cost_tracker_kitchen_daily_cost"

  device = entity_device(hass, entity)
  assert device.name == "Octopus Energy Cost Tracker (Kitchen)"
  assert device.identifiers == {(DOMAIN, "cost-tracker-Kitchen")}


async def test_account_diagnostic_uses_account_service_device(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyAccountDataLastRetrieved(
    hass,
    create_coordinator(),
    ACCOUNT_ID,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_{ACCOUNT_ID}_account_data_last_retrieved"
  assert entity.has_entity_name is True
  assert entity.name == "Data Last Retrieved"
  assert entity.entity_id == "sensor.octopus_energy_account_a_test_data_last_retrieved"

  device = entity_device(hass, entity)
  assert device.name == f"Octopus Energy Account ({ACCOUNT_ID})"
  assert device.identifiers == {(DOMAIN, f"account-{ACCOUNT_ID}")}
