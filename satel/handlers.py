import logging

from . import types, utils

_LOGGER = logging.getLogger(__name__)


# def handlePartitionArmed(mode, msg):
#     partitions = utils.list_set_bits(msg, 4)
#     _LOGGER.debug("Partitions armed in mode %s: %s", mode, partitions)
#     return mode, partitions


# def handleCommandResultEF(msg):
#     status = {}
#     error_code = msg[1:2]

#     if error_code in [b'\x00', b'\xFF']:
#         status = {"status": "OK"}
#     elif error_code == b'\x01':
#         status = {"status": "User code not found"}
#     else:
#         status = {"status": "Error: %s" % error_code}

#     _LOGGER.debug("Received command results: %s: %s", status, utils.toHex(msg))
#     return status


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
