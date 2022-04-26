from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional

from pylutron_leap.api import id_from_href


@dataclass
class IPv4PropertyDefinition:
    Type: str
    IP: Optional[str] = None
    SubnetMask: Optional[str] = None
    Gateway: Optional[str] = None
    DNS1: Optional[str] = None
    DNS2: Optional[str] = None
    DNS3: Optional[str] = None


@dataclass
class IPv6PropertyDefinition:
    UniqueLocalUnicastAddresses: Sequence[str]


@dataclass
class IPLDefinition:
    ProcessorID: int


@dataclass
class ProcessorWhiteListDefinition:
    JWT: str


@dataclass
class ProcessorNetworkInterfaceDefinition:
    MACAddress: str
    IPv4Properties: IPv4PropertyDefinition
    IPv6Properties: IPv6PropertyDefinition


@dataclass
class ProcessorDeviceDefinition:
    href: str
    SerialNumber: int
    NetworkInterfaces: Sequence[ProcessorNetworkInterfaceDefinition]
    IPL: IPLDefinition

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _id: int | None = id_from_href(self.href)
        if _id is not None:
            _ids.append(_id)
        return _ids


@dataclass
class LeapMasterDeviceListBody:
    Devices: Sequence[ProcessorDeviceDefinition]
    SignedWhiteList: ProcessorWhiteListDefinition

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        for item in self.Devices:
            _ids.extend(item.related_ids())

        return _ids
