import logging
import string

from . import types, utils

_LOGGER = logging.getLogger(__name__)


# def handlePartitionArmed(mode, msg):
  # partitions = utils.list_set_bits(msg, 4)
  # _LOGGER.debug("Partitions armed in mode %s: %s", mode, partitions)
  # return mode, partitions


# def handleCommandResultEF(msg):
  # status = {}
  # error_code = msg[1:2]

  # if error_code in [b'\x00', b'\xFF']:
  #   status = {"status": "OK"}
  # elif error_code == b'\x01':
  #   status = {"status": "User code not found"}
  # else:
  #   status = {"status": "Error: %s" % error_code}

  # _LOGGER.debug("Received command results: %s: %s", status, utils.toHex(msg))
  # return status


def handleGetDeviceNameEE(response: types.Response) -> types.DeviceDescription:
  if response.msgId == b"\xEF":
    return types.DeviceDescription(False)
  deviceName = response.msg[3 : 3 + 16]
  deviceFunction = response.msg[2:3]
  return types.DeviceDescription(
    True, deviceName.decode("cp1250"), int.from_bytes(deviceFunction, "big")
  )


def handleGetETHMVersion(response: types.Response) -> types.ETHMVersionInfo:
  byte11 = int.from_bytes(response.msg[11:12], "little")
  return types.ETHMVersionInfo(
    bytes.decode(response.msg[0:11], "cp1250"),
    byte11 & 0x01 == 0x01,
    byte11 & 0x02 == 0x02,
  )


def handleGetINTEGRAVersion(response: types.Response) -> types.INTEGRAVersionInfo:
  byte0 = int.from_bytes(response.msg[0:1], "little")
  byte12 = int.from_bytes(response.msg[12:13], "little")
  byte13 = int.from_bytes(response.msg[13:14], "little")
  return types.INTEGRAVersionInfo(
    bytes.decode(response.msg[1:12], "cp1250"),
    types.IntegraType(byte0),
    byte12,
    byte13 == 0xFF,
  )


def handleListObjects(response: types.Response, numerOfBytes: int):
  mask = response.msg[:numerOfBytes]
  return utils.list_set_bits(mask, numerOfBytes)


def handleListZones(response: types.Response):
  return handleListObjects(response, 16)


def handleListPartitions(response: types.Response):
  return handleListObjects(response, 4)


def handleListOutputs(response: types.Response):
  return handleListObjects(response, 16)


def handleListDataAvailable(response: types.Response):
  return handleListObjects(response, 6)


def handleListEvents(response: types.Response) -> types.Event:
  eventRecord = []
  for i in range(8):
    eventRecord.append(int.from_bytes(response.msg[i:i+1], "little"))
  timeInMinutes = ((eventRecord[2] & 0b00001111) << 8) | eventRecord[3]
  hourMinute = divmod(timeInMinutes, 60)

  return types.Event(
    id = response.msg[8:11],
    yearMark = (eventRecord[0] & 0b11000000) >> 6,
    recordNotEmpty = (eventRecord[0] & 0b00100000) > 0,
    eventPresent = (eventRecord[0] & 0b00010000) > 0,
    monitoringStatusS1 = (eventRecord[0] & 0b00001100) >> 2,
    monitoringStatusS2 = (eventRecord[0] & 0b00000011),
    eventClass = (eventRecord[1] & 0b11100000) >> 5,
    dayOfMonth = (eventRecord[1] & 0b00011111),
    month = (eventRecord[2] & 0b11110000) >> 4,
    hour = hourMinute[0],
    minute = hourMinute[1],
    partition = (eventRecord[4] & 0b11111000) >> 3,
    restore = (eventRecord[4] & 0b00000100) > 0,
    eventCode = ((eventRecord[4] & 0b00000011) << 8) | eventRecord[5],
    source = eventRecord[6],
    object = (eventRecord[7] & 0b11100000) >> 5,
    userControlNumber = (eventRecord[7] & 0b00011111)
  )

def handleGetEventDescription(response: types.Response) -> types.EventDescription:
  longDescription: bool = (int.from_bytes(response.msg[0:2], "big") & 0x8000) > 0
  kindLong: int = int.from_bytes(response.msg[2:3], "big")
  kindShort: int = int.from_bytes(response.msg[3:5], "big")
  descriptionLength = 46 if longDescription else 16
  descriptionFullText = bytes.decode(response.msg[5:5+descriptionLength], "cp1250")
  return types.EventDescription(
    kindLong,
    kindShort,
    text = descriptionFullText.strip()
  )
