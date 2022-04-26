from __future__ import annotations

from collections.abc import Coroutine, Sequence
from logging import getLogger
from typing import TYPE_CHECKING, List, Optional, cast

from pylutron_leap.api import id_from_href
from pylutron_leap.api.area import (
    AreaDefinition,
    AreaStatusType,
    LeapAreaDefinitionBody,
)
from pylutron_leap.api.enum import (
    CommuniqueType,
    MessageBodyTypeEnum,
    OccupiedStateEnum,
)
from pylutron_leap.api.message import (
    LeapAreaStatusBody,
    LeapMessage,
    LeapMessageHeader,
    LeapMultiAreaDefinitionBody,
    LeapMultiAreaStatusBody,
)
from pylutron_leap.models import BaseModel
from pylutron_leap.models.device import Device
from pylutron_leap.models.zone import Zone

if TYPE_CHECKING:
    from pylutron_leap.session import LeapSession

logger = getLogger(__name__)

AreaBodyTypes: list[MessageBodyTypeEnum] = [
    MessageBodyTypeEnum.OneAreaDefinition,
    MessageBodyTypeEnum.OneAreaStatus,
    MessageBodyTypeEnum.MultipleAreaDefinition,
    MessageBodyTypeEnum.MultipleAreaStatus,
    MessageBodyTypeEnum.MultipleAreaSummaryDefinition,
]


class Area(BaseModel):
    instances: Sequence[Area] = []
    default_session: LeapSession
    subscribe_callbacks: Sequence[Coroutine[None, LeapMessage, None]] = []

    def __init__(self, leap_id: int, session: LeapSession = None):
        super().__init__(leap_id, session)

        self.name: Optional[str] = None
        self.parent: Optional[int] = None
        self._sort: Optional[int] = None
        self._leaf: Optional[bool] = None

        self.occupancy: Optional[OccupiedStateEnum] = None
        self.current_scene: Optional[str] = None
        self.level: Optional[int] = None
        self.instantaneous_power: Optional[int] = None
        self.instantaneous_max_power: Optional[int] = None

    def _update_status(self, status: AreaStatusType) -> None:
        if status.OccupancyStatus is not None:
            self.occupancy = status.OccupancyStatus
        if status.CurrentScene is not None:
            # Need to add some sort of lookup here
            self.current_scene = status.CurrentScene.href
        if status.Level is not None:
            self.level = status.Level
        if status.InstantaneousPower is not None:
            self.instantaneous_power = status.InstantaneousPower
        if status.InstantaneousMaxPower is not None:
            self.instantaneous_max_power = status.InstantaneousMaxPower

    @property
    def href(self) -> str:
        return f"/area/{self.leap_id}"

    @property
    def is_leaf(self) -> bool:
        return self._leaf is True

    @property
    def sort_order(self) -> int:
        return self._sort or -1

    def __repr__(self) -> str:
        return f"Area <Name: {self.name}, ID: {self.leap_id}>"

    def _update_definition(self, defn: AreaDefinition) -> None:
        if defn.Name is not None:
            self.name = defn.Name
        if defn.Parent is not None:
            self.parent = id_from_href(defn.Parent.href)
        if defn.SortOrder is not None:
            self._sort = defn.SortOrder
        if defn.IsLeaf is not None:
            self._leaf = defn.IsLeaf

    @classmethod
    def get_or_create_area(cls, session: LeapSession, leap_id: int) -> Area:
        _areas = list(filter(lambda x: x.leap_id == leap_id, session.areas))
        if len(_areas):
            assert len(_areas) == 1
            logger.debug(f"Found area: {_areas[0]}")
            return _areas[0]
        else:
            _area = Area(leap_id, session)
            session.models.append(_area)

            # async def update_def(a: Area = _area):
            #     a.refresh_definition

            # get_running_loop().call_soon(update_def)

            logger.debug(f"Created new area: {_area}")
            return _area

    @classmethod
    def can_handle_response(cls, response: LeapMessage) -> bool:
        return response.Header.MessageBodyType in AreaBodyTypes

    @classmethod
    def handle_response(
        cls, session: LeapSession, response: LeapMessage
    ) -> Sequence[Area]:

        _ids: list[int]
        _area: Area
        entry: AreaStatusType | AreaDefinition
        _updated_areas: List[Area] = []

        if response.Header.MessageBodyType == MessageBodyTypeEnum.OneAreaStatus:

            _ids = response.related_ids()
            assert len(_ids) == 1

            _area = cls.get_or_create_area(session, _ids[0])
            _area._update_status(cast(LeapAreaStatusBody, response.Body).AreaStatus)

            _updated_areas.append(_area)

        elif response.Header.MessageBodyType == MessageBodyTypeEnum.MultipleAreaStatus:
            for entry in cast(LeapMultiAreaStatusBody, response.Body).AreaStatuses:
                _ids = entry.related_ids()
                if len(_ids) == 0:
                    logger.error("Protocol error! No area status bodies found")
                    return _updated_areas

                _area = cls.get_or_create_area(session, _ids[0])
                _area._update_status(entry)
                _updated_areas.append(_area)
        elif (
            response.Header.MessageBodyType
            == MessageBodyTypeEnum.MultipleAreaDefinition
        ):
            for entry in cast(LeapMultiAreaDefinitionBody, response.Body).Areas:
                _ids = entry.related_ids()
                if len(_ids) == 0:
                    logger.error("Protocol error! No area status bodies found")
                    return _updated_areas

                _area = cls.get_or_create_area(session, _ids[0])
                _area._update_definition(entry)
                _updated_areas.append(_area)

        return _updated_areas

    async def refresh_definition(self):

        _updated_areas: List[Area] = []
        _msg = LeapMessage(
            CommuniqueType=CommuniqueType.ReadRequest,
            Header=LeapMessageHeader(Url=self.href),  # type: ignore
        )  # type: ignore

        _response = await self.session.request(_msg)

        LeapAreaStatusBody
        if _response.Header.MessageBodyType == MessageBodyTypeEnum.OneAreaDefinition:
            for entry in cast(LeapAreaDefinitionBody, _response.Body).Area:

                _id = id_from_href(entry.href)

                if _id is None:
                    logger.error(f"Something went wrong parsing Area ID: {entry.href}")
                    continue

                _area = Area.get_or_create_area(self.session, _id)
                _area._update_definition(entry)
                _updated_areas.append(_area)

        return _updated_areas

    def get_children(self) -> Sequence[Area]:
        return filter(
            lambda x: x.parent == self.leap_id, self.session.areas
        )  # type: ignore

    def get_parent(self) -> Area | None:
        _areas = list(filter(lambda x: x.leap_id == self.parent, self.session.areas))
        if len(_areas):
            return _areas[0]
        return None

    async def refresh_state(self) -> None:
        """
        {
            "CommuniqueType": "ReadResponse",
            "Header": {
                "MessageBodyType": "OneAreaStatus",
                "StatusCode": "200 OK",
                "Url": "/area/5668/status",
                "ClientTag": "bf04b5e9-c596-4116-94dc-94d90e403848"
            },
            "Body": {
                "AreaStatus": {
                    "href": "/area/5668/status",
                    "OccupancyStatus": "Unknown",
                    "CurrentScene": null
                }
            }
        }
        """
        _msg = LeapMessage(  # type: ignore
            CommuniqueType=CommuniqueType.ReadRequest,
            Header=LeapMessageHeader(Url=f"/area/{self.leap_id}/status"),  # type: ignore
        )

        _response: LeapMessage = await self.session.request(_msg)
        if _response.Header.MessageBodyType != MessageBodyTypeEnum.OneAreaStatus:
            logger.error("Invalid message type for area status update!")
            return

        _body = cast(LeapAreaStatusBody, _response.Body)
        self.occupancy = _body.AreaStatus.OccupancyStatus
        self.level = _body.AreaStatus.Level
        self.instantaneous_power = _body.AreaStatus.InstantaneousPower
        self.instantaneous_max_power = _body.AreaStatus.InstantaneousMaxPower

        if _body.AreaStatus.CurrentScene is not None:
            self.current_scene = _body.AreaStatus.CurrentScene.href

        logger.debug("Received updated state for area")

    async def get_devices(self) -> Sequence[Device]:
        if not self.is_leaf:
            return []

        _msg = LeapMessage(  # type: ignore
            CommuniqueType=CommuniqueType.ReadRequest,
            Header=LeapMessageHeader(  # type: ignore
                Url=f'/device?where=AssociatedArea.href:"{self.href}"'
            ),
        )

        _response: LeapMessage = await self.session.request(_msg)
        self.devices: Sequence[Device] = []
        if Device.can_handle_response(_response):
            self.devices = Device.handle_response(self.session, _response)
        else:
            logger.error("Invalid message type for assicated device status update!")

        return self.devices
        """
                request:
                {"CommuniqueType":"ReadRequest","Header":{"Url":"/device?where=AssociatedArea.href:\"/area/407\""}}

                response:
                    {
                        "CommuniqueType": "ReadResponse",
                        "Header": {
                            "MessageBodyType": "MultipleDeviceDefinition",
                            "StatusCode": "200 OK",
                            "Url": "/device?where=AssociatedArea.href:\"/area/407\""
                        },
                        "Body": {
                            "Devices": [
                            {
                                "href": "/device/835",
                                "Name": "Fan Control 1",
                                "Parent": { "href": "/project" },
                                "SerialNumber": 012345678,
                                "ModelNumber": "RRD-2ANF",
                                "DeviceType": "Unknown",
                                "AssociatedArea": { "href": "/area/407" },
                                "LinkNodes": [{ "href": "/device/835/linknode/836" }],
                                "DeviceClass": { "HexadecimalEncoding": "4070101" },
                                "AddressedState": "Addressed"
                            },
                            {
                                "href": "/device/854",
                                "Name": "Fan Control 2",
                                "Parent": { "href": "/project" },
                                "SerialNumber": 012345678,
                                "ModelNumber": "RRD-2ANF",
                                "DeviceType": "Unknown",
                                "AssociatedArea": { "href": "/area/407" },
                                "LinkNodes": [{ "href": "/device/854/linknode/855" }],
                                "DeviceClass": { "HexadecimalEncoding": "4070101" },
                                "AddressedState": "Addressed"
                            },
                            {
                                "href": "/device/1934",
                                "Name": "Dimmer",
                                "Parent": { "href": "/project" },
                                "SerialNumber": 012345678,
                                "ModelNumber": "RRD-PRO",
                                "DeviceType": "Unknown",
                                "AssociatedArea": { "href": "/area/407" },
                                "LinkNodes": [{ "href": "/device/1934/linknode/1935" }],
                                "DeviceClass": { "HexadecimalEncoding": "4520101" },
                                "AddressedState": "Addressed"
                            },
                            {
                                "href": "/device/2167",
                                "Name": "Device 001",
                                "Parent": { "href": "/project" },
                                "SerialNumber": 012345678,
                                "ModelNumber": "LRF2-OCR2B-P",
                                "DeviceType": "Unknown",
                                "AssociatedArea": { "href": "/area/407" },
                                "LinkNodes": [{ "href": "/device/2167/linknode/2168" }],
                                "DeviceClass": { "HexadecimalEncoding": "6080101" },
                                "AddressedState": "Addressed"
                            },
                            {
                                "href": "/device/4167",
                                "Name": "Desk Keypad",
                                "Parent": { "href": "/project" },
                                "SerialNumber": 012345678,
                                "ModelNumber": "RR-T5RL",
                                "DeviceType": "SeeTouchTabletopKeypad",
                                "AssociatedArea": { "href": "/area/407" },
                                "LinkNodes": [{ "href": "/device/4167/linknode/4168" }],
                                "DeviceClass": { "HexadecimalEncoding": "1040301" },
                                "AddressedState": "Addressed"
                            },
                            {
                                "href": "/device/5323",
                                "Name": "Device 001",
                                "Parent": { "href": "/project" },
                                "SerialNumber": 012345678,
                                "ModelNumber": "RR-15APS-1",
                                "DeviceType": "Unknown",
                                "AssociatedArea": { "href": "/area/407" },
                                "LinkNodes": [{ "href": "/device/5323/linknode/5324" }],
                                "DeviceClass": { "HexadecimalEncoding": "4150301" },
                                "AddressedState": "Addressed"
                            }
                            ]
                        }
                    }


                    or

        {
          "CommuniqueType": "ReadResponse",
          "Header": {
            "MessageBodyType": "MultipleDeviceDefinition",
            "StatusCode": "200 OK",
            "Url": "/device?where=AssociatedArea.href:\"/area/117\""
          },
          "Body": {
            "Devices": [
              {
                "href": "/device/128",
                "Name": "Enclosure Device 001",
                "Parent": { "href": "/project" },
                "SerialNumber": 012345678,
                "ModelNumber": "JanusProcRA3",
                "DeviceType": "RadioRa3Processor",
                "AssociatedArea": { "href": "/area/117" },
                "OwnedLinks": [
                  { "href": "/link/130", "LinkType": "RF" },
                  { "href": "/link/5407", "LinkType": "ClearConnectTypeX" }
                ],
                "LinkNodes": [
                  { "href": "/device/128/linknode/129" },
                  { "href": "/device/128/linknode/5408" }
                ],
                "FirmwareImage": {
                  "Firmware": { "DisplayName": "21.07.20f000" },
                  "Installed": {
                    "Year": 2022,
                    "Month": 2,
                    "Day": 28,
                    "Hour": 15,
                    "Minute": 17,
                    "Second": 15,
                    "Utc": "-6:00:00"
                  }
                },
                "DeviceFirmwarePackage": {
                  "Package": { "DisplayName": "001.016.000r000" }
                },
                "NetworkInterfaces": [{ "MACAddress": "30:e2:83:01:23:45" }],
                "Databases": [{ "href": "/database/@Project", "Type": "Project" }],
                "DeviceClass": { "HexadecimalEncoding": "81b0101" },
                "AddressedState": "Addressed",
                "IsThisDevice": true
              },
              {
                "href": "/device/6436",
                "Name": "virtual keypad",
                "Parent": { "href": "/project" },
                "ModelNumber": "Homeowner Keypad",
                "DeviceType": "HomeownerKeypad",
                "AssociatedArea": { "href": "/area/117" },
                "LinkNodes": [{ "href": "/device/6436/linknode/6438" }],
                "DeviceClass": { "HexadecimalEncoding": "11f0101" },
                "AddressedState": "Unaddressed"
              }
            ]
          }
        }
        """

    async def get_zones(self) -> Sequence[Zone]:
        """
        Request:
            {"CommuniqueType":"ReadRequest","Header":{"Url":"/area/407/associatedzone/status/expanded"}}
        Response:
            {
            "CommuniqueType": "ReadResponse",
            "Header": {
                "MessageBodyType": "MultipleZoneExpandedStatus",
                "StatusCode": "200 OK",
                "Url": "/area/407/associatedzone/status/expanded"
            },
            "Body": {
                "ZoneExpandedStatuses": [
                    {
                        "href": "/zone/842/status",
                        "FanSpeed": "Off",
                        "StatusAccuracy": "Good",
                        "Zone": {
                            "href": "/zone/842",
                            "Name": "Fan1",
                            "ControlType": "FanSpeed",
                            "Category": { "Type": "CeilingFan", "IsLight": false },
                            "AssociatedArea": { "href": "/area/407" },
                            "SortOrder": 0
                        }
                    },...
                ]
            }
            }
        """
        if not self.is_leaf:
            return []

        _msg = LeapMessage(  # type: ignore
            CommuniqueType=CommuniqueType.ReadRequest,
            Header=LeapMessageHeader(  # type: ignore
                Url=f"{self.href}/associatedzone/status/expanded"
            ),
        )

        _response: LeapMessage = await self.session.request(_msg)
        self.zones: Sequence[Zone] = []
        if Zone.can_handle_response(_response):
            self.zones = Zone.handle_response(self.session, _response)
        else:
            logger.error("Invalid message type for expanded zone status update!")

        return self.zones
