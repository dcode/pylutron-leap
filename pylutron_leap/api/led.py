from dataclasses import dataclass
from typing import Optional

from pylutron_leap.api import HRef, id_from_href
from pylutron_leap.api.enum import LEDState


@dataclass
class LEDStatusType:
    State: LEDState
    href: str
    LED: Optional[HRef] = None

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _id: int | None = id_from_href(self.href)
        if _id is not None:
            _ids.append(_id)
        return _ids


@dataclass
class LeapLEDBody:
    LEDStatus: Optional[LEDStatusType] = None
