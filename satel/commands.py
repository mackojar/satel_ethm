import logging

from . import types, utils

_LOGGER = logging.getLogger(__name__)


def setOutputState(code, output_id, state):
  code_bytes = utils.getCodeBytes(code)
  mode_command = 0x88 if state else 0x89
  command = utils.generate_query(
    mode_command.to_bytes(1, "big") + code_bytes + utils.output_bytes(output_id)
  )
  return command


def listOutputStates():
  return [types.Command.OUTPUTS_STATE.value]


def listDataAvailable():
  return b"\x7F\x00"


def listObjects(command: types.Command):
  return [command.value]


def listZonesViolation():
  return listObjects(types.Command.ZONES_VIOLATION)


def getDeviceName(objectType: types.ObjectType, objectNumber):
  return [0xEE, objectType.value, objectNumber]


def getETHMVersion():
  return [0x7C]


def getINTEGRAVersion():
  return [0x7E]


def listEvents(lastEventIdx: bytes = None):
  if lastEventIdx is None:
    lastEventIdx = types.LAST_EVENT_INDEX
  return [types.Command.LIST_EVENTS.value] + list(lastEventIdx)

def getEventDescription(event: types.Event, longDescription: bool):
  descriptionIndicator = 0b10000000 if longDescription else 0
  restoreMarker = 0b00000100 if event.restore else 0
  return [
    types.Command.GET_EVENT_TEXT.value,
    (descriptionIndicator 
      | restoreMarker
      | (event.eventCode >> 8)),
    event.eventCode & 0xFF
  ]

"""Does not work!!!???"""
def waitForEvents():
  return b"\x7F\x01\xDC\x99\x80\x00\x04\x00\x00\x00\x00\x00\x00"
