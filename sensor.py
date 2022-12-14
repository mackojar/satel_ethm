import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .types import SatelConfigEntry, SatelObjectDescription, ZoneState
from . import SatelCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SatelCoordinator = hass.data[DOMAIN][entry.entry_id]
    satelConfigEntry: SatelConfigEntry = entry.data
    device = satelConfigEntry["device"]
    zones = []
    for zoneDescription in satelConfigEntry["zones"].values():
        zones.append(ZoneEntity(hass, coordinator, device, zoneDescription))
    outputs = []
    for outputDescription in satelConfigEntry["outputs"].values():
        outputs.append(OutputEntity(coordinator, device, outputDescription))
    partitions = []
    for partitionDescription in satelConfigEntry["partitions"].values():
        partitions.append(PartitionEntity(coordinator, device, partitionDescription))
    async_add_entities(zones + outputs + partitions, True)


class ZoneEntity(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = "alarm.input"
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_should_poll = True
    _attr_state_class = None
    _attr_icon = "mdi:motion-sensor"

    _satelId: int
    _isAlarm: bool = False
    _hass: HomeAssistant

    def __init__(self, hass: HomeAssistant, coordinator: SatelCoordinator, device: DeviceInfo, zoneDescription: SatelObjectDescription):
        super().__init__(coordinator)
        self._attr_unique_id = "{domain}.zone.{id}".format(domain=DOMAIN, id=zoneDescription["id"])
        self._attr_name = zoneDescription["description"].strip()
        self._attr_device_info = device
        self._satelId = zoneDescription["id"]
        self._hass = hass

    @property
    def state(self):
        coordinator: SatelCoordinator = self.coordinator
        state = []
        for zoneState in coordinator.zones.keys():
            if self._satelId in coordinator.zones[zoneState]:
                state.append(zoneState.name)
        if self._isAlarm == False and ZoneState.ALARM.name in state:
            _LOGGER.debug("Send zone_alarm_triggered event for %s", self.name)
            self._isAlarm = True
            self._hass.bus.fire("{domain}_zone_alarm_triggered".format(domain=DOMAIN), {"zone_name": self.name})
        if self._isAlarm == True and (ZoneState.ALARM.name not in state):
            _LOGGER.debug("Send zone_alarm_cleared event for %s", self.name)
            self._isAlarm = False
            self._hass.bus.fire("{domain}_zone_alarm_cleared".format(domain=DOMAIN), {"zone_name": self.name})
        return state


class OutputEntity(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = "alarm.output"
    _attr_should_poll = True
    _attr_icon = "mdi:alarm-light"
    _satelId: int

    def __init__(self, coordinator: SatelCoordinator, device: DeviceInfo, outputDescription: SatelObjectDescription):
        super().__init__(coordinator)
        self._attr_unique_id = "{domain}.output.{id}".format(domain=DOMAIN,id=outputDescription["id"])
        self._attr_name = outputDescription["description"].strip()
        self._attr_device_info = device
        self._satelId = outputDescription["id"]

    @property
    def is_on(self):
        coordinator: SatelCoordinator = self.coordinator
        if self._satelId in coordinator.outputsActive:
           return True
        return False


class PartitionEntity(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = "alarm.partition"
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_should_poll = True
    _attr_state_class = None
    _attr_icon = "mdi:home"
    _satelId: int

    def __init__(self, coordinator: SatelCoordinator, device: DeviceInfo, partitionDescription: SatelObjectDescription):
        super().__init__(coordinator)
        self._attr_unique_id = "{domain}.partition.{id}".format(domain=DOMAIN,id=partitionDescription["id"])
        self._attr_name = partitionDescription["description"].strip()
        self._attr_device_info = device
        self._satelId = partitionDescription["id"]

    @property
    def state(self):
        coordinator: SatelCoordinator = self.coordinator
        state = []
        for partitionState in coordinator.partitions.keys():
            if self._satelId in coordinator.partitions[partitionState]:
                state.append(partitionState.name)
        return state
