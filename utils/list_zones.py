import logging
import satel.commands as commands
import satel.types as types
import satel.handlers as handlers
from satel.satel import Satel

LOGGER = logging.getLogger(__name__)

async def listEnabledZones(satel: Satel):
  for zoneId in range(1,128):
    response = await satel.executeCommand(commands.getDeviceName(types.ObjectType.ZONE, zoneId))
    deviceDescription = handlers.handleGetDeviceNameEE(response)
    if deviceDescription.enabled:
      LOGGER.info("Zone Id: %d, name: %s, function: %d", zoneId, deviceDescription.name, deviceDescription.function)
    else:
      LOGGER.info("Zone Id: %d: Disabled", zoneId)
