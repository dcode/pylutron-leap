from dataclasses import dataclass
from typing import Optional

from pylutron_leap.api import HRef
from pylutron_leap.api.enum import (
    CCOZoneLevel,
    FanSpeedType,
    RecepticalState,
    SwitchedState,
)
from pylutron_leap.api.lighting import ColorTuningStatusType, VibrancyStatusType


@dataclass
class CCOLevelParametersType:
    CCOLevel: CCOZoneLevel


@dataclass
class DimmedLevelParametersType:
    Level: int
    FadeTime: Optional[str] = None


@dataclass
class FanSpeedParametersType:
    FanSpeed: FanSpeedType


@dataclass
class GoToSceneParametersType:
    CurrentScene: HRef


@dataclass
class GroupLightingLevelParametersType:
    Level: Optional[int] = None
    VibrancyStatus: Optional[VibrancyStatusType] = None
    FadeTime: Optional[str] = None
    ColorTuningStatus: Optional[ColorTuningStatusType] = None


@dataclass
class ReceptacleLevelParametersType:
    ReceptacleLevel: RecepticalState


@dataclass
class ShadeLevelParametersType:
    Level: Optional[int] = None


@dataclass
class ShadeWithTiltLevelParametersType:
    Level: Optional[int] = None
    Tilt: Optional[int] = None


@dataclass
class SpectrumTuningLevelParametersType:
    Level: Optional[int] = None
    Vibrancy: Optional[int] = None
    FadeTime: Optional[str] = None
    ColorTuningStatus: Optional[ColorTuningStatusType] = None


@dataclass
class SwitchedLevelParametersType:
    SwitchedLevel: SwitchedState
