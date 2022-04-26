from collections.abc import Sequence
from dataclasses import dataclass
from typing import List, Optional

from pylutron_leap.api import HRef, id_from_href
from pylutron_leap.api.enum import OccupiedStateEnum


@dataclass
class AreaStatusType:
    href: str
    CurrentScene: Optional[HRef] = None
    Level: Optional[int] = None
    OccupancyStatus: Optional[OccupiedStateEnum] = None
    InstantaneousPower: Optional[int] = None
    InstantaneousMaxPower: Optional[int] = None

    def related_ids(self) -> List[int]:
        _ids: List[int] = []
        _id: int | None = id_from_href(self.href)
        if _id is not None:
            _ids.append(_id)
        return _ids


@dataclass
class AreaDefinition:
    href: str
    Name: str
    SortOrder: int
    IsLeaf: bool
    Parent: Optional[HRef] = None
    AsociatedZones: Optional[List[HRef]] = None
    AssociatedControlStations: Optional[List[HRef]] = None

    def related_ids(self) -> List[int]:
        _ids: List[int] = []
        _id: int | None = id_from_href(self.href)
        if _id is not None:
            _ids.append(_id)
        return _ids


@dataclass
class LeapAreaDefinitionBody:
    Area: AreaDefinition

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _ids.extend(self.Area.related_ids())
        return _ids


@dataclass
class LeapAreaStatusBody:
    AreaStatus: AreaStatusType

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _ids.extend(self.AreaStatus.related_ids())
        return _ids


@dataclass
class LeapMultiAreaDefinitionBody:
    Areas: Sequence[AreaDefinition]

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        for item in self.Areas:
            _ids.extend(item.related_ids())
        return _ids


@dataclass
class LeapMultiAreaStatusBody:
    AreaStatuses: Sequence[AreaStatusType]

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        for item in self.AreaStatuses:
            _ids.extend(item.related_ids())

        return _ids
