from collections.abc import Sequence
from dataclasses import dataclass
from typing import Dict, Optional

from pylutron_leap.api import HRef, id_from_href
from pylutron_leap.api.enum import AvailibilityType, BatteryState


@dataclass
class BatteryStatusType:
    LevelState: BatteryState


@dataclass
class Transfers:
    Count: int


@dataclass
class DeviceStatusType:
    href: str
    Availability: Optional[AvailibilityType] = None
    BatteryStatus: Optional[BatteryStatusType] = None
    FailedTransfers: Optional[Transfers] = None

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _id: int | None = id_from_href(self.href)
        if _id is not None:
            _ids.append(_id)
        return _ids


@dataclass
class FirmwareName:
    DisplayName: str


@dataclass
class FirmwareInstalled:
    Year: int
    Month: int
    Day: int
    Hour: int
    Minute: int
    Second: int
    Utc: str


@dataclass
class FirmwareImageDefn:
    Firmware: FirmwareName
    Installed: FirmwareInstalled


@dataclass
class DeviceFirmwarePackageDefn:
    Package: FirmwareName


@dataclass
class DatabaseInfo:
    href: str
    Type: str


@dataclass
class LinkInfo:
    href: str
    LinkType: str  # this can probably be an enum. I've seen RF and ClearConnectTypeX


@dataclass
class DeviceClassType:
    # This should be able to make a lookup to something like dimmer, switch, fan, etc
    HexadecimalEncoding: str


@dataclass
class DeviceDefinition:
    href: str
    Name: str
    Parent: HRef

    SerialNumber: Optional[int] = None
    ModelNumber: Optional[str] = None
    # Make DeviceType an enum? (RadioRa3Processor, VisorControlReceiver, Unknown, SeeTouchHybridKeypad, Pico3ButtonRaiseLower, SunnataDimmer, SunnataSwitch, HomeownerKeypad)
    DeviceType: Optional[str] = None
    # No idea what DeviceRules are
    DeviceRules: Optional[Sequence[HRef]] = None
    FirmwareImage: Optional[FirmwareImageDefn | HRef] = None
    DeviceFirmwarePackage: Optional[DeviceFirmwarePackageDefn] = None
    Databases: Optional[Sequence[DatabaseInfo]] = None
    OwnedLinks: Optional[Sequence[LinkInfo]] = None
    AddressedState: Optional[str] = None
    LinkNodes: Optional[Sequence[HRef]] = None
    IsThisDevice: Optional[bool] = None
    # "NetworkInterfaces": [{"MACAddress": "ab:cd:ef:01:23:45"}]
    NetworkInterfaces: Optional[Sequence[Dict[str, str]]] = None
    DeviceClass: Optional[DeviceClassType] = None

    AssociatedArea: Optional[HRef] = None
    LocalZones: Optional[Sequence[HRef]] = None

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _id: int | None = id_from_href(self.href)
        if _id is not None:
            _ids.append(_id)
        return _ids


@dataclass
class LeapMultiDeviceDefinitionBody:
    """
    This message body is the result of a device lookup by query, such as:
    "/device?where=IsThisDevice:true"
    """

    Devices: Sequence[DeviceDefinition]

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        for item in self.Devices:
            _ids.extend(item.related_ids())

        return _ids


@dataclass
class LeapDeviceBody:
    DeviceStatus: DeviceStatusType

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _ids.extend(self.DeviceStatus.related_ids())

        return _ids


@dataclass
class LeapMultiDeviceBody:
    DeviceStatuses: list[DeviceStatusType]

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        for item in self.DeviceStatuses:
            _ids.extend(item.related_ids())

        return _ids
