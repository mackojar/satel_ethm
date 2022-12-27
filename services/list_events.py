import logging
import custom_components.satel_ethm.satel.commands as commands
import custom_components.satel_ethm.satel.types as types
import custom_components.satel_ethm.satel.handlers as handlers
from ..satel.satel import Satel

_LOGGER = logging.getLogger(__name__)

eventDescriptionCache: dict[bytes, types.EventDescription] = {}

async def getEvent(satel: Satel, eventIdx: bytes) -> types.EventData:
  responseListEvents = await satel.executeCommand(commands.listEvents(eventIdx))
  event = handlers.handleListEvents(responseListEvents)
  _LOGGER.debug("Event: %s" % str(event))
  if event.recordNotEmpty:
    listCommand: list(int) = commands.getEventDescription(event, True)
    listCommandBytes = bytes(listCommand)
    eventDescription = eventDescriptionCache.get(listCommandBytes)
    if eventDescription is None:
      responseEventDescription = await satel.executeCommand(listCommand)
      eventDescription = handlers.handleGetEventDescription(responseEventDescription)
      eventDescriptionCache[listCommandBytes] = eventDescription
    _LOGGER.debug("EventDescription: %s" % str(eventDescription))
    return types.EventData(event, eventDescription)
  else:
    return types.EventData(event, None)

async def listEvents(satel: Satel, count: int):
  events: list[types.EventData] = []
  lastEventIdx: bytes = types.LAST_EVENT_INDEX
  for _ in range(count):
    eventData: types.EventData = await getEvent(satel, lastEventIdx)
    if eventData.event.recordNotEmpty:
      lastEventIdx = eventData.event.id
      events.append(eventData)
    else:
      break
  return events
