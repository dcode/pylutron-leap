from dataclasses import dataclass
from typing import Optional

# from dataclasses import dataclass
from pylutron_leap.api.enum import CommandType
from pylutron_leap.api.parameters import (
    CCOLevelParametersType,
    DimmedLevelParametersType,
    FanSpeedParametersType,
    GoToSceneParametersType,
    GroupLightingLevelParametersType,
    ReceptacleLevelParametersType,
    ShadeLevelParametersType,
    ShadeWithTiltLevelParametersType,
    SpectrumTuningLevelParametersType,
    SwitchedLevelParametersType,
)


@dataclass
class LeapCommand:
    CommandType: CommandType
    SwitchedLevelParameters: Optional[SwitchedLevelParametersType] = None
    DimmedLevelParameters: Optional[DimmedLevelParametersType] = None
    ShadeLevelParameters: Optional[ShadeLevelParametersType] = None
    ShadeWithTiltLevelParameters: Optional[ShadeWithTiltLevelParametersType] = None
    SpectrumTuningLevelParameters: Optional[SpectrumTuningLevelParametersType] = None
    CCOLevelParameters: Optional[CCOLevelParametersType] = None
    ReceptacleLevelParameters: Optional[ReceptacleLevelParametersType] = None
    FanSpeedParameters: Optional[FanSpeedParametersType] = None
    GroupLightingLevelParameters: Optional[GroupLightingLevelParametersType] = None
    GoToSceneParameters: Optional[GoToSceneParametersType] = None


@dataclass
class LeapCommandBody:
    Command: LeapCommand

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        return _ids
