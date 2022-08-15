"""The satel_ethm integration."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
import logging
import custom_components.satel_ethm.satel.commands as commands
import custom_components.satel_ethm.satel.handlers as handlers
import custom_components.satel_ethm.satel.types as satelTypes
import custom_components.satel_ethm.types as types
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_HOST, CONF_PORT
from .const import DOMAIN
from .satel.satel import Satel

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.ALARM_CONTROL_PANEL, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    satelConfigEntry: types.SatelConfigEntry = entry.data

    """ Workaround for storing entity config but? """
    device = satelConfigEntry["device"]
    if type(device["identifiers"]) == list:
        ids = device["identifiers"][0]
        device["identifiers"] = {(ids[0], ids[1])}
    """ End of workaround """
    coordinator = SatelCoordinator(hass, satelConfigEntry)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


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
        ZoneStateDefinition(types.ZoneState.BYPASS, satelTypes.Command.ZONES_BYPASS, "bypassed")
    ]

    partitionCommands: list[PartitionStateDefinition] = [
        PartitionStateDefinition(types.PartitionState.ARMED, satelTypes.Command.PARTITIONS_ARMED, "armed"),
        PartitionStateDefinition(types.PartitionState.ALARM, satelTypes.Command.PARTITIONS_ALARM, "alarm"),
        PartitionStateDefinition(types.PartitionState.FIRE_ALARM, satelTypes.Command.PARTITIONS_FIRE_ALARM, "fire alarm"),
        PartitionStateDefinition(types.PartitionState.ALARM_MEMORY, satelTypes.Command.PARTITIONS_ALARM_MEMORY, "alarm memory"),
        PartitionStateDefinition(types.PartitionState.FIRE_ALARM_MEMORY, satelTypes.Command.PARTITIONS_FIRE_ALARM_MEMORY, "fire alarm memory"),
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
        _LOGGER.info("SatelCoordinator _async_update_data")
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
