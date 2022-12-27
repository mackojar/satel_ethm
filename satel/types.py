from dataclasses import dataclass
from enum import Enum, unique

LAST_EVENT_INDEX: bytes = b'\xFF\xFF\xFF'

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
  ZONES_NO_VIOLATION_TROUBLE = 0x07
  ZONES_LONG_VIOLATION_TROUBLE = 0x08
  ZONES_ISOLATE = 0x26
  ZONES_MASKED = 0x28
  ZONES_MASKED_MEMORY = 0x29

  PARTITIONS_ARMED = 0x0A
  PARTITIONS_ARMED_MODE_1 = 0x2a
  PARTITIONS_ARMED_MODE_2 = 0x0b
  PARTITIONS_ARMED_MODE_3 = 0x0c
  PARTITIONS_FIRST_CODE_ENTERED = 0x0d
  PARTITIONS_ENTRY_TIME = 0x0e
  PARTITIONS_EXIT_TIME_LONG = 0x0f # > 10s
  PARTITIONS_EXIT_TIME_SHORT = 0x10 # < 10s
  PARTITIONS_TEMP_BLOCKED = 0x11
  PARTITIONS_BLOCKED_GUARD = 0x12
  PARTITIONS_ALARM = 0x13
  PARTITIONS_FIRE_ALARM = 0x14
  PARTITIONS_ALARM_MEMORY = 0x15
  PARTITIONS_FIRE_ALARM_MEMORY = 0x16
  PARTITIONS_VIOLATED_ZONES = 0x25
  PARTITIONS_VERIFIED_ALARMS = 0x27
  PARTITIONS_WARNING_ALARMS = 0x2B

  OUTPUTS_STATE = 0x17

  LIST_EVENTS = 0x8C
  GET_EVENT_TEXT = 0x8F

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

@dataclass
class Event:
  id: bytes

  yearMark: int
  month: int
  dayOfMonth: int
  hour: int
  minute: int

  recordNotEmpty: bool
  eventPresent: bool
  monitoringStatusS1: int
  monitoringStatusS2: int
  userControlNumber: int

  eventClass: int
  partition: int
  restore: bool
  eventCode: int
  source: int
  object: int

@dataclass
class EventDescription:
  kindLong: int
  kindShort: int
  text: str

@dataclass
class EventData:
  event: Event
  eventDescription: EventDescription
  