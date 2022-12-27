import logging
import time
import satel.commands as commands
import satel.types as types
import satel.handlers as handlers
from satel.satel import Satel

LOGGER = logging.getLogger(__name__)

OBJ_CONFIG = [
  (types.ObjectType.ZONE, 16, types.Command.ZONES_VIOLATION, "zone violated"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_TAMPER, "zone tampered"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_ALARM, "zone alarm"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_TAMPER_ALARM, "zone tamper alarm"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_ALARM_MEMORY, "zone alarm memory"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_TAMPER_ALARM_MEMORY, "zone tamper alarm memory"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_BYPASS, "zone bypassed"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_NO_VIOLATION_TROUBLE, "zone no-violation trouble"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_LONG_VIOLATION_TROUBLE, "zone long-violation trouble"),  
  (types.ObjectType.ZONE, 16, types.Command.ZONES_ISOLATE, "zone isolated"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_MASKED, "zone masked"),
  (types.ObjectType.ZONE, 16, types.Command.ZONES_MASKED_MEMORY, "zone masked memory"),

  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_ARMED, "partition armed"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_ALARM, "partition alarm"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_FIRE_ALARM, "partition fire alarm"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_ALARM_MEMORY, "partition alarm memory"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_FIRE_ALARM_MEMORY, "partition fire alarm memory"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_ARMED_MODE_1, "partition armed mode 1"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_ARMED_MODE_2, "partition armed mode 2"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_ARMED_MODE_3, "partition armed mode 3"),
  # (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_FIRST_CODE_ENTERED, "partition 1st code entered"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_ENTRY_TIME, "partition entry time"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_EXIT_TIME_LONG, "partition exit time (>10s)"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_EXIT_TIME_SHORT, "partition exit time (<10s)"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_TEMP_BLOCKED, "partition temporary blocked"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_BLOCKED_GUARD, "partition blocked guard"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_VIOLATED_ZONES, "partition violated zones"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_VERIFIED_ALARMS, "partition verified alarms"),
  (types.ObjectType.PARTITION, 4, types.Command.PARTITIONS_WARNING_ALARMS, "partition warning alarms"),

  (types.ObjectType.OUTPUT, 4, types.Command.OUTPUTS_STATE, "output")
]

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

async def handleMarkedData(satel, markedCommands):
  for objConfig in OBJ_CONFIG:
    command: bytes = objConfig[2]
    if isCommandMarked(command, markedCommands):
      objType: types.ObjectType = objConfig[0]
      expectedBytes: int = objConfig[1]
      msg: str = objConfig[3]
      await listObjects(satel, objType, command, expectedBytes, msg)

async def monitorAlarm(satel: Satel):
  while True:
    await satel.connect()
    newData = await satel.executeCommand(commands.listDataAvailable())
    markedCommands = handlers.handleListDataAvailable(newData)
    LOGGER.debug("Marked commands: %s", str(markedCommands))
    await handleMarkedData(satel, markedCommands)
    # await satel.disconnect()
    time.sleep(5)
