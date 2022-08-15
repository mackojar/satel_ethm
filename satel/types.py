from dataclasses import dataclass
from enum import Enum, unique
import string


@unique
class AlarmState(Enum):
    ARMED_MODE0 = 0
    ARMED_MODE1 = 1
    ARMED_MODE2 = 2
    ARMED_MODE3 = 3
    ARMED_SUPPRESSED = 4
    ENTRY_TIME = 5
    EXIT_COUNTDOWN_OVER_10 = 6
    EXIT_COUNTDOWN_UNDER_10 = 7
    TRIGGERED = 8
    TRIGGERED_FIRE = 9
    DISARMED = 10


@unique
class ObjectType(Enum):
    PARTITION = 0
    ZONE = 1
    USER = 2
    EXPANDER_LCD = 3
    OUTPUT = 4
    ZONE_PARTITION = 5
    TIMER = 6
    TELEPHONE = 7
    OBJECT = 15
    PARTITION_OBJECT = 16
    OUTPUT_WITH_DURATION = 17
    PARTITION_OBJECT_OPTIONS = 18


@unique
class Command(Enum):
    ZONES_VIOLATION = 0x00
    ZONES_TAMPER = 0x01
    ZONES_ALARM = 0x02
    ZONES_TAMPER_ALARM = 0x03
    ZONES_ALARM_MEMORY = 0x04
    ZONES_TAMPER_ALARM_MEMORY = 0x05
    ZONES_BYPASS = 0x06
    PARTITIONS_ARMED = 0x0A
    PARTITIONS_ALARM = 0x13
    PARTITIONS_FIRE_ALARM = 0x14
    PARTITIONS_ALARM_MEMORY = 0x15
    PARTITIONS_FIRE_ALARM_MEMORY = 0x16
    OUTPUTS_STATE = 0x17


@dataclass
class Response:
    msgId: bytes
    msg: bytes


@dataclass
class DeviceDescription:
    enabled: bool
    name: str = ""
    function: int = 0


@dataclass
class ETHMVersionInfo:
    version: str
    zones32bytes: bool
    trouble8bytes: bool


@unique
class IntegraType(Enum):
    INTEGRA_24 = 0
    INTEGRA_32 = 1
    INTEGRA_64 = 2
    INTEGRA_128 = 3
    INTEGRA_128WRL_SIM300 = 4
    INTEGRA_128WRL_LEON = 132
    INTEGRA_64Plus = 66
    INTEGRA_128Plus = 67
    INTEGRA_256Plus = 72


@dataclass
class INTEGRAVersionInfo:
    version: str
    type: IntegraType
    language: int
    settingsInFlash: bool
