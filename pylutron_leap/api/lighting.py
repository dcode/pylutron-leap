from dataclasses import dataclass
from typing import Optional

from .enum import EnableStateType


@dataclass
class HSVTuningLevelType:
    Hue: int
    Saturation: int


@dataclass
class VibrancyStatusType:
    Vibrancy: Optional[int] = None
    AutoVibrancy: Optional[EnableStateType] = None


@dataclass
class WhiteTuningLevelType:
    Kelvin: int


@dataclass
class WhiteTuningLevelRangeType:
    Min: int
    Max: int


@dataclass
class XYTuningLevelType:
    X: float
    Y: float


@dataclass
class ColorTuningPropertiesType:
    WhiteTuningLevelRange: Optional[WhiteTuningLevelRangeType]


@dataclass
class ColorTuningStatusType:
    HSVTuningLevel: Optional[HSVTuningLevelType] = None
    WhiteTuningLevel: Optional[WhiteTuningLevelType] = None
    XYTuningLevel: Optional[XYTuningLevelType] = None
