"""Config flow for satel_ethm integration."""
from __future__ import annotations
import logging
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
import custom_components.satel_ethm.types as types
import custom_components.satel_ethm.satel.commands as commands
import custom_components.satel_ethm.satel.handlers as handlers
import custom_components.satel_ethm.satel.types as satelTypes
from .const import DOMAIN
from .satel.satel import Satel

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="192.168.1.200"): str,
        vol.Required(CONF_PORT, default=33107): int,
    }
)

# inputs=40
# outputs=25
# partitions=2


async def _async_load_objects(
        satel: Satel,
        objectIdRange: range, 
        objectType: satelTypes.ObjectType,
        filterObjects: function = lambda x: True) -> dict[int, types.SatelObjectDescription]:

    objects: dict[int, types.SatelObjectDescription] = {}
    for objectId in objectIdRange:
        response = await satel.executeCommand(commands.getDeviceName(objectType, objectId))
        deviceDescription = handlers.handleGetDeviceNameEE(response)
        if filterObjects(deviceDescription) and deviceDescription.enabled:
            _LOGGER.debug("Object Id: %d, name: %s", objectId, deviceDescription.name)
            objects[objectId] = types.SatelObjectDescription(id=objectId, description=deviceDescription.name)
        else:
            _LOGGER.debug("Object filtered out, Id: %d: Enabled: %s, Function: %d", objectId, deviceDescription.enabled, deviceDescription.function)
    return objects


async def _async_init_satel(satel: Satel) -> types.SatelConfigEntry:
    _LOGGER.info("Load Satel configuration")
    """ ETHM Version is not used """
    # response = await self._satel.executeCommand(commands.getETHMVersion())
    # ethmVersionInfo = handlers.handleGetETHMVersion(response)
    response = await satel.executeCommand(commands.getINTEGRAVersion())
    integraVersionInfo = handlers.handleGetINTEGRAVersion(response)
    device = DeviceInfo(
        identifiers = {(DOMAIN, integraVersionInfo.version)},
        name = "INTEGRA",
        manufacturer = "Satel",
        model = integraVersionInfo.type.name,
        sw_version = integraVersionInfo.version
    )
    zones = await _async_load_objects(satel, range(1,50), satelTypes.ObjectType.ZONE)
    outputs = await _async_load_objects(satel, range(1,30), satelTypes.ObjectType.OUTPUT, lambda objectDescription: objectDescription.function != 0)
    partitions = await _async_load_objects(satel, range(1,5), satelTypes.ObjectType.PARTITION)
    return types.SatelConfigEntry(
        device=device,
        zones=zones,
        outputs=outputs,
        partitions=partitions)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> types.SatelConfigEntry:
    try:
        host = data[CONF_HOST]
        port = data[CONF_PORT]
        satel = Satel(host, port, hass.loop)
        await satel.connect()
        satelConfigEntry = await _async_init_satel(satel)
        satelConfigEntry[CONF_HOST] = host
        satelConfigEntry[CONF_PORT] = port
        return satelConfigEntry
    except Exception as e:
        _LOGGER.exception("Error retrieving information from Satel")
        raise CannotConnect(e)
    finally:
        await satel.disconnect()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        errors = {}
        try:
            satelConfigEntry = await validate_input(self.hass, user_input)
            return self.async_create_entry(title=satelConfigEntry["device"]["model"], data=satelConfigEntry)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
