import asyncio
import logging
from sqlite3 import connect

from . import types, utils

_LOGGER = logging.getLogger(__name__)


class Satel:
    def __init__(self, host, port, loop):
        self._host = host
        self._port = port
        self._loop = loop
        self._reader = None
        self._writer = None

    @property
    def connected(self):
        return self._writer and self._reader

    async def disconnect(self):
        try:
            _LOGGER.debug("Closing connection...")
            if self._writer != None:
                self._writer.close()
                await self._writer.drain()
        except Exception as e:
            pass
        finally:
            _LOGGER.debug("Clear connection information")
            self._reader = None
            self._writer = None

    async def connect(self):
        if self.connected:
            _LOGGER.debug("Already connected to Satel")
            return
        try:
            _LOGGER.debug("Connecting to Satel...")
            self._reader, self._writer = await asyncio.open_connection(
                self._host, self._port
            )
            _LOGGER.debug("Connected to Satel")
        except Exception as e:
            _LOGGER.error("Connection error: %s." % e)
            await self.disconnect()
            raise e

    async def executeCommand(self, command: bytes) -> types.Response:
        try:
            request = utils.generate_query(command)
            await self._send_data(request)
            return await self._receive_response()
        except Exception as e:
            _LOGGER.error("Error executing command: %s", e)
            await self.disconnect()
            raise e

    async def _send_data(self, data):
        _LOGGER.debug("Sending data: %s (len: %d)", utils.toHex(data), len(data))
        self._writer.write(data)
        await self._writer.drain()

    async def _receive_response(self) -> types.Response:
        _LOGGER.debug("Waiting for response...")
        resp = await self._read_data()
        if not resp:
            raise ConnectionError()
        msgId = resp[0:1]
        msg = resp[1:]
        return types.Response(msgId, msg)

    async def _read_data(self):
        data = await self._reader.readuntil(b"\xFE\x0D")
        _LOGGER.debug("Received data: %s", utils.toHex(data))
        return utils.verify_and_strip(data)
