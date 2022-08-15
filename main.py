import asyncio
import logging
import time
import satel.commands as commands
import satel.types as types
import satel.handlers as handlers
from satel.satel import Satel

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
LOGGER = logging.getLogger(__name__)


async def listEnabledZones(satel: Satel):
  for zoneId in range(1,128):
    response = await satel.executeCommand(commands.getDeviceName(types.ObjectType.ZONE, zoneId))
    deviceDescription = handlers.handleGetDeviceNameEE(response)
    if deviceDescription.enabled:
      LOGGER.info("Zone Id: %d, name: %s, function: %d", zoneId, deviceDescription.name, deviceDescription.function)
    else:
      LOGGER.info("Zone Id: %d: Disabled", zoneId)


async def listViolatedZones(satel: Satel):
  response = await satel.executeCommand(commands.listZonesViolation())
  violatedZones = handlers.handleListZones(response)
  LOGGER.info("Zones violated: %s", violatedZones)
  for zoneId in violatedZones:
    response = await satel.executeCommand(commands.getDeviceName(types.ObjectType.ZONE, zoneId))
    deviceDescription = handlers.handleGetDeviceNameEE(response)
    LOGGER.info("Zone name: %s, function: %d", deviceDescription.name, deviceDescription.function)


async def listObjects(satel: Satel, objectType: types.ObjectType, command: bytes, expectedBytes: int, description: str):
  response = await satel.executeCommand(commands.listObjects(command))
  markedObjects = handlers.handleListObjects(response, expectedBytes)
  LOGGER.info("Objects for %s: %s", description, markedObjects)
  for objectId in markedObjects:
    response = await satel.executeCommand(commands.getDeviceName(objectType, objectId))
    deviceDescription = handlers.handleGetDeviceNameEE(response)
    LOGGER.info("Object name (%s): %s", description, deviceDescription.name)


async def listObjectDescription(satel: Satel, objectType: types.ObjectType, objectRange: range):
  for objectId in objectRange:
    response = await satel.executeCommand(commands.getDeviceName(objectType, objectId))
    deviceDescription = handlers.handleGetDeviceNameEE(response)
    LOGGER.info("Object description: %s", deviceDescription)


def isCommandMarked(command: types.Command, markedCommands: list):
  return command.value + 1 in markedCommands


async def monitorAlarm(satel: Satel):
  while True:
    await satel.connect()
    newData = await satel.executeCommand(commands.listDataAvailable())
    markedData = handlers.handleListDataAvailable(newData)
    if isCommandMarked(types.Command.ZONES_VIOLATION, markedData):
      await listObjects(satel, types.ObjectType.ZONE, types.Command.ZONES_VIOLATION, 16, "zone violated")
    if isCommandMarked(types.Command.PARTITIONS_ARMED, markedData):
      await listObjects(satel, types.ObjectType.PARTITION, types.Command.PARTITIONS_ARMED, 4, "partitions armed")
    if isCommandMarked(types.Command.PARTITIONS_ALARM, markedData):
      await listObjects(satel, types.ObjectType.PARTITION, types.Command.PARTITIONS_ALARM, 4, "partitions alarmed")
    if isCommandMarked(types.Command.OUTPUTS_STATE, markedData):
      await listObjects(satel, types.ObjectType.OUTPUT, types.Command.OUTPUTS_STATE, 4, "output")
    # await satel.disconnect()
    time.sleep(5)


async def main():
  try:
    loop = asyncio.get_event_loop()
    satel = Satel("192.168.1.200", 33107, loop)
    await satel.connect()
    
    # response = await satel.executeCommand(commands.getETHMVersion())
    # ethmVersionInfo = handlers.handleGetETHMVersion(response)
    # LOGGER.info("ethm: %s", ethmVersionInfo)

    # response = await satel.executeCommand(commands.getINTEGRAVersion())
    # integraVersionInfo = handlers.handleGetINTEGRAVersion(response)
    # LOGGER.info("integra: %s", integraVersionInfo)

    # response = await satel.executeCommand(commands.waitForEvents())
    # await listViolatedZones(satel)
    # await listEnabledZones(satel)
    # await monitorAlarm(satel)
    await listObjectDescription(satel, types.ObjectType.ZONE, range(1,20))

  except Exception as e:
      LOGGER.error("Processing error: %s." % e, exc_info=1)


asyncio.run(main())
