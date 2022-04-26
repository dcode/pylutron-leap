from dataclasses import dataclass
from typing import Optional

from pylutron_leap.api import HRef, id_from_href
from pylutron_leap.api.enum import (
    CCOZoneLevel,
    FanSpeedType,
    RecepticalState,
    SwitchedState,
    ZoneControlType,
    ZoneType,
)
from pylutron_leap.api.lighting import ColorTuningStatusType


@dataclass
class ZoneCategoryType:
    IsLight: bool
    Type: str
    SubType: str


@dataclass
class ZonePhaseSettings:
    href: str
    Direction: str


@dataclass
class ZoneTuningSettings:
    href: str
    LowEndTrim: float
    HighEndTrim: float


@dataclass
class ZoneDefinitionType:
    href: str
    Name: str
    SortOrder: int
    ControlType: Optional[ZoneType]
    Category: Optional[ZoneCategoryType]
    Device: Optional[HRef]

    ColorTuningProperties: Optional[ColorTuningStatusType]
    PhaseSettings: Optional[ZonePhaseSettings]
    TuningSettings: Optional[ZoneTuningSettings]
    AssociatedArea: Optional[HRef]
    AssociatedFacade: Optional[HRef]


@dataclass
class ZoneStatusType:
    href: str
    SwitchedLevel: Optional[SwitchedState] = None
    Level: Optional[int] = None
    Tilt: Optional[int] = None
    Vibrancy: Optional[int] = None
    ColorTuningStatus: Optional[ColorTuningStatusType] = None
    CCOLevel: Optional[CCOZoneLevel] = None
    ReceptacleLevel: Optional[RecepticalState] = None
    FanSpeed: Optional[FanSpeedType] = None
    Zone: Optional[ZoneDefinitionType] = None
    StatusAccuracy: Optional[str] = None  # TODO: Make this an enum, so far seen "Good"
    Availability: Optional[
        str
    ] = None  # TODO: Make this an enum, so far seen "Available"

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _id: int | None = id_from_href(self.href)
        if _id is not None:
            _ids.append(_id)
        return _ids


@dataclass
class LeapZoneBody:
    ZoneStatus: ZoneStatusType

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _ids.extend(self.ZoneStatus.related_ids())

        return _ids


@dataclass
class LeapZoneDefinitionBody:
    href: str
    Name: str
    ControlType: ZoneControlType
    Category: ZoneCategoryType
    Device: HRef


@dataclass
class LeapMultipleZoneExpandedStatusBody:
    ZoneExpandedStatuses: list[ZoneStatusType]


@dataclass
class LeapMultiZoneBody:
    ZoneStatuses: list[ZoneStatusType]

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        for item in self.ZoneStatuses:
            _ids.extend(item.related_ids())

        return _ids


@dataclass
class LeapZoneTypeGroupBody:
    ZoneTypeGroupStatus: ZoneStatusType

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _ids.extend(self.ZoneTypeGroupStatus.related_ids())

        return _ids


@dataclass
class LeapMultiZoneTypeGroupBody:
    ZoneTypeGroupStatuses: list[ZoneStatusType]

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        for item in self.ZoneTypeGroupStatuses:
            _ids.extend(item.related_ids())

        return _ids
