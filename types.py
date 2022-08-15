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

@unique
class OutputState(Enum):
    INACTIVE = 1
    ACTIVE = 2

@unique
class PartitionState(Enum):
    ARMED = 1
    ALARM = 2
    FIRE_ALARM = 3
    ALARM_MEMORY = 4
    FIRE_ALARM_MEMORY = 5


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
