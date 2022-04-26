from dataclasses import dataclass
from typing import Optional

from . import HRef
from .enum import LoadShedState


@dataclass
class SystemLoadSheddingStatusType:
    State: Optional[LoadShedState] = None
    SystemLoadShedding: Optional[HRef] = None


@dataclass
class LeapLoadShedBody:
    SystemLoadSheddingStatus: SystemLoadSheddingStatusType
