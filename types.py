from enum import Enum, unique
from typing import TypedDict
from homeassistant.helpers.entity import DeviceInfo
from .satel.types import DeviceDescription


@unique
class ZoneState(Enum):
  VIOLATED = 0
  TAMPER = 1
  ALARM = 2
  TAMPER_ALARM = 3
  ALARM_MEMORY = 4
  TAMPER_ALARM_MEMORY = 5
  BYPASS = 6
  NO_VIOLATION_TROUBLE = 7
  LONG_VIOLATION_TROUBLE = 8
  ISOLATE = 9
  MASKED = 10
  MASKED_MEMORY = 11

@unique
class PartitionState(Enum):
  ARMED = 1
  ALARM = 2
  FIRE_ALARM = 3
  ALARM_MEMORY = 4
  FIRE_ALARM_MEMORY = 5
  ARMED_MODE_1 = 6
  ARMED_MODE_2 = 7
  ARMED_MODE_3 = 8
  FIRST_CODE_ENTERED = 9
  ENTRY_TIME = 10
  EXIT_TIME_LONG = 11
  EXIT_TIME_SHORT = 12
  TEMP_BLOCKED = 13
  BLOCKED_GUARD = 14
  VIOLATED_ZONES = 15
  VERIFIED_ALARMS = 16
  WARNING_ALARMS = 17


class SatelObjectDescription(TypedDict):
  id: int
  description: DeviceDescription


class SatelConfigEntry(TypedDict):
  host: str
  port: int
  device: DeviceInfo
  zones: dict[int, SatelObjectDescription]
  outputs: dict[int, SatelObjectDescription]
  partitions: dict[int, SatelObjectDescription]
