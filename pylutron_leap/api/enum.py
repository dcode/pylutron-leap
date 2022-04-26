from enum import Enum, EnumMeta, auto


class DefaultEnumMeta(EnumMeta):
    """
    Metaclass to set the default value to the first item in
    the enumeration. Adopted from https://stackoverflow.com/a/44867928
    """

    default = object()

    def __call__(cls, value=default, *args, **kwargs):
        if value is DefaultEnumMeta.default:
            # Assume the first enum is default
            return next(iter(cls))
        return super().__call__(value, *args, **kwargs)


class ValuesEnum(Enum, metaclass=DefaultEnumMeta):
    @classmethod
    def items(cls):
        return [x.name for x in cls]


class AreaMode(ValuesEnum):
    Unknown = auto()
    DimLevel = auto()
    Switched = auto()


class AvailibilityType(ValuesEnum):
    Unknown = auto()
    Available = auto()
    Mixed = auto()
    Unavailable = auto()


class BatteryState(ValuesEnum):
    Unknown = auto()
    Bad = auto()
    Good = auto()


class ButtonEventType(ValuesEnum):
    Unknown = auto()
    LongHold = auto()
    MultiTap = auto()
    Press = auto()
    Release = auto()


class ButtonEventState(ValuesEnum):
    MultiTap = auto()
    PressAndHold = auto()
    PressAndRelease = auto()
    Release = auto()


class ButtonMode(ValuesEnum):
    Auto = auto()
    MultiTap = auto()
    PressRelease = auto()


class CCOZoneLevel(ValuesEnum):
    Closed = auto()
    Open = auto()


class CommandType(ValuesEnum):
    Unknown = auto()
    Activate = auto()
    GoToCCOLevel = auto()
    GoToDimmedLevel = auto()
    GoToFanSpeed = auto()
    GoToGroupLightingLevel = auto()
    GoToReceptacleLevel = auto()
    GoToScene = auto()
    GoToShadeLevel = auto()
    GoToShadeLevelWithTilt = auto()
    GoToSpectrumTuningLevel = auto()
    GoToSwitchedLevel = auto()
    Lower = auto()
    LowerTilt = auto()
    Raise = auto()
    RaiseTilt = auto()
    Reboot = auto()
    Stop = auto()
    StopTilt = auto()


class CommuniqueType(ValuesEnum):
    Unknown = auto()
    CreateRequest = auto()
    CreateResponse = auto()
    ExceptionResponse = auto()
    ReadRequest = auto()
    ReadResponse = auto()
    SubscribeRequest = auto()
    SubscribeResponse = auto()
    UpdateRequest = auto()
    UpdateResponse = auto()


class ContextTypeEnum(ValuesEnum):
    Unknown = auto()
    Application = auto()


class EmergencyStateEnum(ValuesEnum):
    Inactive = auto()
    Active = auto()


class EnableStateType(ValuesEnum):
    Disabled = auto()
    Enabled = auto()


class FanSpeedType(ValuesEnum):
    Unknown = auto()
    Off = auto()
    Low = auto()
    Medium = auto()
    MediumHigh = auto()
    High = auto()


class LEDState(ValuesEnum):
    Unknown = auto()
    On = auto()
    Off = auto()
    NormalFlash = auto()
    RapidFlash = auto()


class LoadShedState(ValuesEnum):
    Disabled = auto()
    Enabled = auto()


class MessageBodyTypeEnum(ValuesEnum):
    Unknown = auto()
    AdvancedToggleProgrammingModel = auto()
    DualActionProgrammingModel = auto()
    ExceptionDetail = auto()
    MultipleAreaDefinition = auto()
    MultipleAreaStatus = auto()
    MultipleAreaSummaryDefinition = auto()
    MultipleButtonGroupDefinition = auto()
    MultipleButtonStatusEvent = auto()
    MultipleCCOLevelAssignmentDefinition = auto()
    MultipleControlStationDefinition = auto()
    MultipleDeviceDefinition = auto()
    MultipleDeviceStatus = auto()
    MultipleDimmedLevelAssignmentDefinition = auto()
    MultipleEmergencyDefinition = auto()
    MultipleEmergencyStatus = auto()
    MultipleFanSpeedAssignmentDefinition = auto()
    MultipleOccupancyGroupDefinition = auto()
    MultipleOccupancyGroupStatus = auto()
    MultipleOccupancySensorStatus = auto()
    MultipleProgrammingModelDefinition = auto()
    MultipleReceptacleLevelAssignmentDefinition = auto()
    MultipleSpectrumTuningLevelAssignmentDefinition = auto()
    MultipleSwitchedLevelAssignmentDefinition = auto()
    MultipleVirtualButtonDefinition = auto()
    MultipleVirtualButtonDefinitionSummary = auto()
    MultipleZoneDefinition = auto()
    MultipleZoneExpandedStatus = auto()
    MultipleZoneStatus = auto()
    MultipleZoneTypeGroupStatus = auto()
    OneAreaDefinition = auto()
    OneAreaStatus = auto()
    OneButtonDefinition = auto()
    OneButtonGroupDefinition = auto()
    OneButtonStatusEvent = auto()
    OneClientSettingDefinition = auto()
    OneDeviceStatus = auto()
    OneEmergencyStatus = auto()
    OneLEDDefinition = auto()
    OneLEDStatus = auto()
    OneLoginDefinition = auto()
    OneMasterDeviceListDefinition = auto()
    OneOccupancySensorDefinition = auto()
    OneOccupancySensorStatus = auto()
    OnePingResponse = auto()
    OnePresetDefinition = auto()
    OneProgrammingModelDefinition = auto()
    OneProjectDefinition = auto()
    OneSystemLoadSheddingStatus = auto()
    OneVirtualButtonDefinition = auto()
    OneZoneDefinition = auto()
    OneZoneStatus = auto()
    OneZoneTypeGroupStatus = auto()
    SingleActionProgrammingModel = auto()
    SingleSceneRaiseProgrammingModel = auto()


class OccupiedStateEnum(ValuesEnum):
    Unknown = auto()
    Occupied = auto()
    Unoccupied = auto()


class RecepticalState(ValuesEnum):
    Off = auto()
    On = auto()


class SessionPermissions(ValuesEnum):
    Unauthorized = auto()
    ControlAndMonitor = auto()
    Admin = auto()


class ShadeMode(ValuesEnum):
    Unknown = auto()
    Lift = auto()
    LiftAndTilt = auto()


class SpectrumTuningType(ValuesEnum):
    Unknown = auto()
    HueAndSaturation = auto()
    WhiteTuning = auto()
    ColorXY = auto()
    Vibrancy = auto()


class SwitchedState(ValuesEnum):
    Unknown = auto()
    Off = auto()
    On = auto()


class ZoneControlType(ValuesEnum):
    Unknown = auto()
    Switched = auto()
    Dimmed = auto()
    FanSpeed = auto()


class ZoneMode(ValuesEnum):
    Unknown = auto()
    CCO = auto()
    DimLevel = auto()
    Receptical = auto()
    Switched = auto()


class ZoneType(ValuesEnum):
    zone = auto()
    zonetypegroup = auto()
