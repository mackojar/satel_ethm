"""The satel_ethm integration."""
from __future__ import annotations
import logging
import voluptuous as vol
import custom_components.satel_ethm.types as types
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .coordinator import SatelCoordinator
from .const import DOMAIN, LIST_EVENTS_COUNT

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.ALARM_CONTROL_PANEL, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  satelConfigEntry: types.SatelConfigEntry = entry.data

  """ Workaround for storing entity config: list is converted in HA """
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
  # HA service can not return any value: disable the service
  # hass.services.async_register(DOMAIN, "list_events", coordinator.list_events_service)
  return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
    hass.data[DOMAIN].pop(entry.entry_id)
  return unload_ok

