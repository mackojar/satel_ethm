import asyncio
import logging
from satel.satel import Satel
import utils.list_zones as list_zones
import utils.list_events as list_events
import utils.monitor_alarm as monitor_alarms


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
LOGGER = logging.getLogger(__name__)

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

    # await listObjectDescription(satel, types.ObjectType.ZONE, range(1,20))
    # await monitor_alarms.monitorAlarm(satel)
    events = await list_events.listEvents(satel, 10)
    LOGGER.info("Events:")
    for eventData in events:
      LOGGER.info("Event: %s: EventCls/Code: %d/%d, Obj: %d, P: %d, Src: %d" % 
        (eventData.eventDescription.text, 
        eventData.event.eventClass,
        eventData.event.eventCode,
        eventData.event.object, 
        eventData.event.partition,
        eventData.event.source))

    # response = await satel.executeCommand(commands.waitForEvents())


  except Exception as e:
    LOGGER.error("Processing error: %s." % e, exc_info=1)


asyncio.run(main())
