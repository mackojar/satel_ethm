"""The satel_ethm integration."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
import logging
# import threading
import custom_components.satel_ethm.satel.commands as commands
import custom_components.satel_ethm.satel.handlers as handlers
import custom_components.satel_ethm.satel.types as satelTypes
import custom_components.satel_ethm.types as types
import custom_components.satel_ethm.services.list_events as list_events
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_HOST, CONF_PORT
from .const import LIST_EVENTS_COUNT
from .satel.satel import Satel

_LOGGER = logging.getLogger(__name__)

@dataclass
class ZoneStateDefinition:
  state: types.ZoneState
  command: satelTypes.Command
  description: str

@dataclass
class PartitionStateDefinition:
  state: types.PartitionState
  command: satelTypes.Command
  description: str

class SatelCoordinator(DataUpdateCoordinator):
    
  _satel: Satel = None
  # _lock = threading.Lock()

  outputsActive: list[int] = []    
  zones: dict[types.ZoneState, list[int]] = {}
  partitions: dict[types.PartitionState, list[int]] = {}

  zoneCommands: list[ZoneStateDefinition] = [
    ZoneStateDefinition(types.ZoneState.VIOLATED, satelTypes.Command.ZONES_VIOLATION, "violated"),
    ZoneStateDefinition(types.ZoneState.TAMPER, satelTypes.Command.ZONES_TAMPER, "tampered"),
    ZoneStateDefinition(types.ZoneState.ALARM, satelTypes.Command.ZONES_ALARM, "alarmed"),
    ZoneStateDefinition(types.ZoneState.TAMPER_ALARM, satelTypes.Command.ZONES_TAMPER_ALARM, "tamper alarm"),
    ZoneStateDefinition(types.ZoneState.ALARM_MEMORY, satelTypes.Command.ZONES_ALARM_MEMORY, "alarm memory"),
    ZoneStateDefinition(types.ZoneState.TAMPER_ALARM_MEMORY, satelTypes.Command.ZONES_TAMPER_ALARM_MEMORY, "tamper alarm memory"),
    ZoneStateDefinition(types.ZoneState.BYPASS, satelTypes.Command.ZONES_BYPASS, "bypassed"),
    ZoneStateDefinition(types.ZoneState.NO_VIOLATION_TROUBLE, satelTypes.Command.ZONES_BYPASS, "no-violation troubles"),
    ZoneStateDefinition(types.ZoneState.LONG_VIOLATION_TROUBLE, satelTypes.Command.ZONES_BYPASS, "long-violation troubles"),
    ZoneStateDefinition(types.ZoneState.ISOLATE, satelTypes.Command.ZONES_BYPASS, "isolated"),
    ZoneStateDefinition(types.ZoneState.MASKED, satelTypes.Command.ZONES_BYPASS, "masked"),
    ZoneStateDefinition(types.ZoneState.MASKED_MEMORY, satelTypes.Command.ZONES_BYPASS, "masked memory")
  ]

  partitionCommands: list[PartitionStateDefinition] = [
    PartitionStateDefinition(types.PartitionState.ARMED, satelTypes.Command.PARTITIONS_ARMED, "armed"),
    PartitionStateDefinition(types.PartitionState.ALARM, satelTypes.Command.PARTITIONS_ALARM, "alarm"),
    PartitionStateDefinition(types.PartitionState.FIRE_ALARM, satelTypes.Command.PARTITIONS_FIRE_ALARM, "fire alarm"),
    PartitionStateDefinition(types.PartitionState.ALARM_MEMORY, satelTypes.Command.PARTITIONS_ALARM_MEMORY, "alarm memory"),
    PartitionStateDefinition(types.PartitionState.FIRE_ALARM_MEMORY, satelTypes.Command.PARTITIONS_FIRE_ALARM_MEMORY, "fire alarm memory"),
    PartitionStateDefinition(types.PartitionState.ARMED_MODE_1, satelTypes.Command.PARTITIONS_ARMED_MODE_1, "armed mode 1"),
    PartitionStateDefinition(types.PartitionState.ARMED_MODE_2, satelTypes.Command.PARTITIONS_ARMED_MODE_2, "armed mode 2"),
    PartitionStateDefinition(types.PartitionState.ARMED_MODE_3, satelTypes.Command.PARTITIONS_ARMED_MODE_3, "armed mode 3"),
    # Does not work correctly: returns empty response
    # PartitionStateDefinition(types.PartitionState.FIRST_CODE_ENTERED, satelTypes.Command.PARTITIONS_FIRST_CODE_ENTERED, "first code entered"),
    PartitionStateDefinition(types.PartitionState.ENTRY_TIME, satelTypes.Command.PARTITIONS_ENTRY_TIME, "entry time"),
    PartitionStateDefinition(types.PartitionState.EXIT_TIME_LONG, satelTypes.Command.PARTITIONS_EXIT_TIME_LONG, "exit time long"),
    PartitionStateDefinition(types.PartitionState.EXIT_TIME_SHORT, satelTypes.Command.PARTITIONS_EXIT_TIME_SHORT, "exit time short"),
    PartitionStateDefinition(types.PartitionState.TEMP_BLOCKED, satelTypes.Command.PARTITIONS_TEMP_BLOCKED, "temporary blocked"),
    PartitionStateDefinition(types.PartitionState.BLOCKED_GUARD, satelTypes.Command.PARTITIONS_BLOCKED_GUARD, "blocked for guard"),
    PartitionStateDefinition(types.PartitionState.VIOLATED_ZONES, satelTypes.Command.PARTITIONS_VIOLATED_ZONES, "violated zones"),
    PartitionStateDefinition(types.PartitionState.VERIFIED_ALARMS, satelTypes.Command.PARTITIONS_VERIFIED_ALARMS, "verified alarms"),
    PartitionStateDefinition(types.PartitionState.WARNING_ALARMS, satelTypes.Command.PARTITIONS_WARNING_ALARMS, "warning alarms"),
  ]


  def __init__(self, hass: HomeAssistant, satelConfigEntry: types.SatelConfigEntry):
    super().__init__(hass, _LOGGER,
      name="Satel",
      update_interval=timedelta(seconds=10),
    )
    host = satelConfigEntry[CONF_HOST]
    port = satelConfigEntry[CONF_PORT]
    self._satel = Satel(host=host, port=port, loop=hass.loop)

    for zoneCommand in self.zoneCommands:
      self.zones[zoneCommand.state] = []
    for partitionCommand in self.partitionCommands:
      self.partitions[partitionCommand.state] = []

  def _isCommandMarked(self, command: types.Command, markedCommands: list):
    return command.value + 1 in markedCommands


  async def _async_update_data(self):
    # self._lock.acquire()
    _LOGGER.debug("SatelCoordinator _async_update_data")
    await self._satel.connect()
    newData = await self._satel.executeCommand(commands.listDataAvailable())
    markedData = handlers.handleListDataAvailable(newData)
    if self._isCommandMarked(satelTypes.Command.OUTPUTS_STATE, markedData):
      await self._async_list_outputs_active()
    for zoneCommand in self.zoneCommands:
      if self._isCommandMarked(zoneCommand.command, markedData):
        self.zones[zoneCommand.state] = await self._async_list_zones_status([zoneCommand.command.value], zoneCommand.description)
    for partitionCommand in self.partitionCommands:
      if self._isCommandMarked(partitionCommand.command, markedData):
        self.partitions[partitionCommand.state] = await self._async_list_partitions_status([partitionCommand.command.value], partitionCommand.description)
    # self._lock.release()

  async def _async_list_outputs_active(self):
    response = await self._satel.executeCommand(commands.listOutputStates())
    self.outputsActive = handlers.handleListOutputs(response)
    _LOGGER.debug("Outputs active: %s", self.outputsActive)


  async def _async_list_zones_status(self, command: list[int], description: str):
    response = await self._satel.executeCommand(command)
    zonesMarked = handlers.handleListZones(response)
    _LOGGER.debug("Zones %s: %s", description, zonesMarked)
    return zonesMarked


  async def _async_list_partitions_status(self, command: list[int], description: str):
    response = await self._satel.executeCommand(command)
    partitionsMarked = handlers.handleListPartitions(response)
    _LOGGER.debug("Partitions %s: %s", description, partitionsMarked)
    return partitionsMarked


  # async def list_events_service(self, service_call):
  #   self._lock.acquire()
  #   count = service_call.data.get(LIST_EVENTS_COUNT)
  #   _LOGGER.debug("listEvents called: %d" % count)
  #   events =  await list_events.listEvents(self._satel, count)
  #   self._lock.release()
  #   return events
