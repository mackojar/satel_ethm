import logging

from homeassistant.components.alarm_control_panel import (
  AlarmControlPanelEntity,
  AlarmControlPanelEntityFeature,
  CodeFormat,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .types import PartitionState, SatelConfigEntry
from . import SatelCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
  coordinator: SatelCoordinator = hass.data[DOMAIN][entry.entry_id]
  satelConfigEntry: SatelConfigEntry = entry.data
  satelControlPanel = SatelControlPanel(coordinator, satelConfigEntry)
  async_add_entities([satelControlPanel], True)


class SatelControlPanel(CoordinatorEntity, AlarmControlPanelEntity):
  _attr_has_entity_name = True
  _attr_supported_features = (
    AlarmControlPanelEntityFeature.ARM_HOME |
    AlarmControlPanelEntityFeature.ARM_NIGHT |
    AlarmControlPanelEntityFeature.ARM_AWAY)
  _attr_code_arm_required = False
  _attr_code_format = CodeFormat.NUMBER
  _attr_should_poll = True
  _attr_icon = "mdi:alarm-panel"

  numberOfPartitions: int

  def __init__(self, coordinator: SatelCoordinator, satelConfigEntry: SatelConfigEntry):
    self.coordinator = coordinator
    self.coordinator_context = None
    self._attr_device_info = satelConfigEntry["device"]
    self._attr_unique_id = "{domain}.alarm_panel".format(domain=DOMAIN)
    self.numberOfPartitions = len(satelConfigEntry["partitions"])

  @property
  def name(self):
    return "Satel Alarm Panel"

  @property
  def state(self):
    coordinator: SatelCoordinator = self.coordinator
    if len(coordinator.partitions[PartitionState.ALARM]) > 0:
      return "triggered"
    if len(coordinator.partitions[PartitionState.ENTRY_TIME]) > 0:
      return "pending"
    if len(coordinator.partitions[PartitionState.EXIT_TIME_LONG]) > 0:
      return "arming"
    if len(coordinator.partitions[PartitionState.EXIT_TIME_SHORT]) > 0:
      return "arming"
    # if len(coordinator.partitions[PartitionState.FIRST_CODE_ENTERED]) > 0:
    #   return "disarming"
    numberOfArmedPartitions = len(coordinator.partitions[PartitionState.ARMED])
    if numberOfArmedPartitions >= self.numberOfPartitions:
      return "armed_away"
    if numberOfArmedPartitions > 0:
      return "armed_night"
    return "disarmed"

  async def async_alarm_disarm(self, code=None) -> None:
    _LOGGER.info("Send disarm command. Code: %s", code)

  async def async_alarm_arm_home(self, code=None) -> None:
    _LOGGER.info("Send arm home command. Code: %s", code)

  async def async_alarm_arm_night(self, code=None) -> None:
    _LOGGER.info("Send arm night command. Code: %s", code)

  async def async_alarm_arm_away(self, code=None) -> None:
    _LOGGER.info("Send arm away command. Code: %s", code)
