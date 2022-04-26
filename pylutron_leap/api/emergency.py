from dataclasses import dataclass
from typing import Optional

from pylutron_leap.api import HRef
from pylutron_leap.api.enum import EmergencyStateEnum


@dataclass
class EmergencyStatus:
    href: Optional[str] = None
    Emergency: Optional[HRef] = None
    ActiveState: Optional[EmergencyStateEnum] = None


@dataclass
class LeapEmergencyBody:
    EmergencyStatus: EmergencyStatus

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        return _ids


@dataclass
class LeapMultiEmergencyBody:
    EmergencyStatuses: list[EmergencyStatus]
