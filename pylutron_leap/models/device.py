from __future__ import annotations

from collections.abc import Sequence
from logging import getLogger
from typing import TYPE_CHECKING, Dict, List, Optional, cast

from pylutron_leap.api import HRef, id_from_href
from pylutron_leap.api.device import (
    AvailibilityType,
    BatteryStatusType,
    DatabaseInfo,
    DeviceDefinition,
    DeviceFirmwarePackageDefn,
    DeviceStatusType,
    FirmwareImageDefn,
    LeapDeviceBody,
    LeapMultiDeviceBody,
    LeapMultiDeviceDefnBody,
    LinkInfo,
    Transfers,
)
from pylutron_leap.api.enum import MessageBodyTypeEnum
from pylutron_leap.api.message import LeapMessage
from pylutron_leap.models import BaseModel

if TYPE_CHECKING:
    from pylutron_leap.models.area import Area
    from pylutron_leap.models.zone import Zone
    from pylutron_leap.session import LeapSession


logger = getLogger(__name__)

DeviceBodyTypes = [
    MessageBodyTypeEnum.OneDeviceStatus,
    MessageBodyTypeEnum.MultipleDeviceDefinition,
    MessageBodyTypeEnum.MultipleDeviceStatus,
    MessageBodyTypeEnum.OneMasterDeviceListDefinition,
]


class Device(BaseModel):
    def __init__(self, leap_id: int, session: LeapSession = None):
        super().__init__(leap_id, session)

        self.name: Optional[str] = None
        self.parent: Optional[int] = None
        self._sort: Optional[int] = None
        self._leaf: Optional[bool] = None

        # Device Definition Fields
        self.addressed_state: Optional[str] = None
        self.databases: Optional[Sequence[DatabaseInfo]] = None
        self.device_firmware_package: Optional[DeviceFirmwarePackageDefn] = None
        self.device_rules: Optional[Sequence[HRef]] = None
        self.device_type: Optional[str] = None
        self.firmware_image: Optional[FirmwareImageDefn] = None
        self.link_nodes: Optional[Sequence[HRef]] = None
        self.model_number: Optional[str] = None
        self.owned_links: Optional[Sequence[LinkInfo]] = None
        self.serial_number: Optional[int] = None

        # "NetworkInterfaces": [{ "MACAddress": "30:e2:83:01:23:45" }],
        self.network_interfaces: Optional[List[dict[str, str]]] = None
        # "DeviceClass": { "HexadecimalEncoding": "81b0101" },
        self.device_class: Optional[List[dict[str, str]]] = None

        # Device Status Fields
        self.availability: Optional[AvailibilityType] = None
        self.battery_status: Optional[BatteryStatusType] = None
        self.failed_transfers: Optional[Transfers] = None

        # Associations
        self.associated_area: Optional[Area] = None
        self.local_zones: Dict[int, Zone] = {}

    @classmethod
    def get_or_create_device(cls, session: LeapSession, leap_id: int) -> Device:
        _devices = list(filter(lambda x: x.leap_id == leap_id, session.devices))
        if len(_devices):
            assert len(_devices) == 1
            return _devices[0]
        else:
            _device = Device(leap_id, session)
            session.models.append(_device)
            return _device

    def _update_status(self, status: DeviceStatusType) -> None:

        if status.Availability is not None:
            self.availability = status.Availability
        if status.BatteryStatus is not None:
            self.battery_status = status.BatteryStatus
        if status.FailedTransfers is not None:
            self.failed_transfers = status.FailedTransfers

        logger.debug(f"Updated device status of {self.leap_id}")

    def _update_definition(self, defn: DeviceDefinition) -> None:

        if defn.Name is not None:
            self.name = defn.Name
        if defn.Parent is not None:
            self.parent = id_from_href(defn.Parent.href)
        if defn.SerialNumber is not None:
            self.serial_number = defn.SerialNumber
        if defn.ModelNumber is not None:
            self.model_number = defn.ModelNumber
        if defn.DeviceType is not None:
            self.device_type = defn.DeviceType  # Make this an enum?
        if defn.DeviceRules is not None:
            self.device_rules = defn.DeviceRules  # What is this?
        if defn.FirmwareImage is not None:
            self.firmware_image = defn.FirmwareImage
        if defn.DeviceFirmwarePackage is not None:
            self.device_firmware_package = defn.DeviceFirmwarePackage
        if defn.Databases is not None:
            self.databases = defn.Databases
        if defn.OwnedLinks is not None:
            self.owned_links = defn.OwnedLinks
        if defn.AddressedState is not None:
            self.addressed_state = defn.AddressedState
        if defn.LinkNodes is not None:
            self.link_nodes = defn.LinkNodes
        if defn.AssociatedArea is not None:
            _id = id_from_href(defn.AssociatedArea.href)
            if _id is not None:
                self.associated_area = Area.get_or_create_area(self.session, _id)
        if defn.LocalZones is not None:
            for entry in defn.LocalZones:
                _id = id_from_href(entry.href)
                if _id is not None:
                    _zone = Zone.get_or_create_zone(self.session, _id)
                    _zone.device = self
                    self.local_zones[_id] = _zone

    @classmethod
    def can_handle_response(cls, response: LeapMessage) -> bool:
        return response.Header.MessageBodyType in DeviceBodyTypes

    @classmethod
    def handle_response(
        cls, session: LeapSession, response: LeapMessage
    ) -> Sequence[Device]:

        _ids: list[int]
        _device: Device
        entry: DeviceDefinition | DeviceStatusType
        _body: LeapMultiDeviceBody | LeapMultiDeviceDefnBody

        _updated_devices: List[Device] = []

        if response.Header.MessageBodyType == MessageBodyTypeEnum.OneDeviceStatus:

            _ids = response.related_ids()
            assert len(_ids) == 1

            _device = cls.get_or_create_device(session, _ids[0])
            _device._update_status(cast(LeapDeviceBody, response.Body).DeviceStatus)

            _updated_devices.append(_device)

        elif (
            response.Header.MessageBodyType == MessageBodyTypeEnum.MultipleDeviceStatus
        ):
            _body = cast(LeapMultiDeviceBody, response.Body)
            for entry in _body.DeviceStatuses:
                _ids = entry.related_ids()
                assert len(_ids) == 1

                _device = cls.get_or_create_device(session, _ids[0])
                _device._update_status(entry)

                _updated_devices.append(_device)

        elif (
            response.Header.MessageBodyType
            == MessageBodyTypeEnum.MultipleDeviceDefinition
        ):
            _body = cast(LeapMultiDeviceDefnBody, response.Body)
            for entry in _body.Devices:
                _ids = entry.related_ids()
                assert len(_ids) == 1

                _device = cls.get_or_create_device(session, _ids[0])
                _device._update_definition(entry)

                _updated_devices.append(_device)

        return _updated_devices
