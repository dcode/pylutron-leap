from typing import Optional

from pylutron_leap.api.command import LeapCommand, LeapCommandBody
from pylutron_leap.api.enum import (
    CCOZoneLevel,
    CommandType,
    FanSpeedType,
    RecepticalState,
    SwitchedState,
)
from pylutron_leap.api.message import (
    CommuniqueType,
    LeapDirectives,
    LeapMessage,
    LeapMessageHeader,
)
from pylutron_leap.api.parameters import (
    CCOLevelParametersType,
    DimmedLevelParametersType,
    FanSpeedParametersType,
    ReceptacleLevelParametersType,
    SpectrumTuningLevelParametersType,
    SwitchedLevelParametersType,
)
from pylutron_leap.models.area import Area

query_params = {"where": [("IsThisDevice",)]}

"""
Possible queries:

where=
    IsThisDevice:true   -> returns the connected device, i.e. the processor connected over TCP
"""


def get_connected_processor() -> LeapMessage:
    """
    { "CommuniqueType": "ReadRequest",
    "Header": { "Url": "/device?where=IsThisDevice:true" }}
    """
    return LeapMessage(
        CommuniqueType=CommuniqueType.ReadRequest,
        Header=LeapMessageHeader(Url="/device?where=IsThisDevice:true"),
    )


def get_other_devices() -> LeapMessage:
    """
    { "CommuniqueType": "ReadRequest",
    "Header": { "Url": "/device?where=IsThisDevice:false" }}


    returns:

    {
    "CommuniqueType": "ReadResponse",
    "Header": {
        "MessageBodyType": "MultipleDeviceDefinition",
        "StatusCode": "200 OK",
        "Url": "/device?where=IsThisDevice:false"
    },
    "Body": {
        "Devices": [
            {
                "Name": "Position 2",
                "DeviceType": "Unknown",
                "AssociatedArea": { "href": "/area/6176" },
                "href": "/device/1835",
                "SerialNumber": 012345678,
                "Parent": { "href": "/project" },
                "ModelNumber": "RRD-PRO",
                "LocalZones": [{ "href": "/zone/1845" }],
                "LinkNodes": [{ "href": "/device/1835/linknode/1836" }],
                "DeviceClass": { "HexadecimalEncoding": "4520101" },
                "AddressedState": "Addressed"
            },
    """
    return LeapMessage(
        CommuniqueType=CommuniqueType.ReadRequest,
        Header=LeapMessageHeader(Url="/device?where=IsThisDevice:false"),
    )


def get_all_area_subscribe():
    return LeapMessage(
        CommuniqueType=CommuniqueType.SubscribeRequest,
        Header=LeapMessageHeader(Url="/area/status"),
    )


def get_all_zone_subscribe():
    return LeapMessage(
        CommuniqueType=CommuniqueType.SubscribeRequest,
        Header=LeapMessageHeader(
            Url="/zone/status", Directives=LeapDirectives(SuppressMessageBody=True)
        ),
    )


def get_all_zonetypegroup_subscribe():
    return LeapMessage(
        CommuniqueType=CommuniqueType.SubscribeRequest,
        Header=LeapMessageHeader(Url="/zonetypegroup/status"),
    )


def get_zone_createrequest_command(leap_id: int, cmd: CommandType) -> LeapMessage:
    return LeapMessage(
        CommuniqueType=CommuniqueType.CreateRequest,
        Header=LeapMessageHeader(Url=f"/zone/{leap_id}/commandprocessor"),
        Body=LeapCommandBody(Command=LeapCommand(CommandType=cmd)),
    )


def get_zone_createrequest_switchcommand(
    leap_id: int, cmd: CommandType, level: SwitchedState
) -> LeapMessage:
    return LeapMessage(
        CommuniqueType=CommuniqueType.CreateRequest,
        Header=LeapMessageHeader(Url=f"/zone/{leap_id}/commandprocessor"),
        Body=LeapCommandBody(
            Command=LeapCommand(
                CommandType=cmd,
                SwitchedLevelParameters=SwitchedLevelParametersType(
                    SwitchedLevel=level
                ),
            )
        ),
    )


def get_zone_createrequest_ccocommand(
    leap_id: int, cmd: CommandType, level: CCOZoneLevel
) -> LeapMessage:
    return LeapMessage(
        CommuniqueType=CommuniqueType.CreateRequest,
        Header=LeapMessageHeader(Url=f"/zone/{leap_id}/commandprocessor"),
        Body=LeapCommandBody(
            Command=LeapCommand(
                CommandType=cmd,
                CCOLevelParameters=CCOLevelParametersType(CCOLevel=level),
            )
        ),
    )


def get_zone_createrequest_receptaclecommand(
    leap_id: int, cmd: CommandType, level: RecepticalState
) -> LeapMessage:
    return LeapMessage(
        CommuniqueType=CommuniqueType.CreateRequest,
        Header=LeapMessageHeader(Url=f"/zone/{leap_id}/commandprocessor"),
        Body=LeapCommandBody(
            Command=LeapCommand(
                CommandType=cmd,
                ReceptacleLevelParameters=ReceptacleLevelParametersType(
                    ReceptacleLevel=level
                ),
            )
        ),
    )


def get_zone_createrequest_fancommand(
    leap_id: int, cmd: CommandType, level: FanSpeedType
) -> LeapMessage:
    return LeapMessage(
        CommuniqueType=CommuniqueType.CreateRequest,
        Header=LeapMessageHeader(Url=f"/zone/{leap_id}/commandprocessor"),
        Body=LeapCommandBody(
            Command=LeapCommand(
                CommandType=cmd,
                FanSpeedParameters=FanSpeedParametersType(FanSpeed=level),
            )
        ),
    )


def get_zone_createrequest_lightinglevelcommand(
    leap_id: int, cmd: CommandType, level: int
) -> LeapMessage:

    _body: LeapCommandBody = LeapCommandBody(Command=LeapCommand(CommandType=cmd))

    if cmd in [CommandType.GoToDimmedLevel, CommandType.GoToSwitchedLevel]:
        _body.Command.DimmedLevelParameters = DimmedLevelParametersType(Level=level)
    elif cmd in [CommandType.GoToSpectrumTuningLevel]:
        _body.Command.SpectrumTuningLevelParameters = SpectrumTuningLevelParametersType(
            Level=level
        )

    _msg = LeapMessage(
        CommuniqueType=CommuniqueType.CreateRequest,
        Header=LeapMessageHeader(Url=f"/zone/{leap_id}/commandprocessor"),
        Body=_body,
    )

    return _msg


def get_all_occupancy_subscribe() -> LeapMessage:
    return LeapMessage(
        CommuniqueType=CommuniqueType.SubscribeRequest,
        Header=LeapMessageHeader(Url="/occupancygroup/status"),
    )


def get_all_loadshed_subscribe() -> LeapMessage:
    return LeapMessage(
        CommuniqueType=CommuniqueType.SubscribeRequest,
        Header=LeapMessageHeader(Url="/system/loadshedding/status"),
    )


def get_all_emergency_subscribe() -> LeapMessage:
    return LeapMessage(
        CommuniqueType=CommuniqueType.SubscribeRequest,
        Header=LeapMessageHeader(Url="/emergency/status"),
    )


def query_devices_by(
    area: Optional[Area] = None, serial: Optional[str] = None
) -> LeapMessage:
    # {"CommuniqueType":"ReadRequest","Header":{"Url":"/device?where=AssociatedArea.href:\"/area/407\""}}
    _url: str = "/device?"
    if area is not None:
        _url += f'where=Associated.href:"{area.href}"'
    _msg = LeapMessage(
        CommuniqueType=CommuniqueType.ReadRequest, Header=LeapMessageHeader(Url=_url)
    )

    return _msg
