from dataclasses import dataclass

from .enum import OccupiedStateEnum


@dataclass
class OccupancySensorStatusType:
    href: str
    OccupancyStatus: OccupiedStateEnum


@dataclass
class LeapOccupancySensorBody:
    OccupancySensorStatus: OccupancySensorStatusType


@dataclass
class LeapMultiOccupancySensorBody:
    OccupancySensorStatuses: list[OccupancySensorStatusType]
