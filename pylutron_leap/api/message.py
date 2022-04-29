from dataclasses import dataclass
from logging import getLogger
from typing import Optional, Union, cast

import marshmallow_dataclass
from marshmallow import post_dump, pre_load

from pylutron_leap.api import id_from_href
from pylutron_leap.api.area import (
    LeapAreaDefinitionBody,
    LeapAreaStatusBody,
    LeapMultiAreaDefinitionBody,
    LeapMultiAreaStatusBody,
)
from pylutron_leap.api.button import LeapButtonBody, LeapButtonStatusBody
from pylutron_leap.api.command import LeapCommandBody
from pylutron_leap.api.device import (
    LeapDeviceBody,
    LeapMultiDeviceBody,
    LeapMultiDeviceDefinitionBody,
)
from pylutron_leap.api.emergency import LeapEmergencyBody, LeapMultiEmergencyBody
from pylutron_leap.api.enum import CommuniqueType, MessageBodyTypeEnum
from pylutron_leap.api.loadshed import LeapLoadShedBody
from pylutron_leap.api.login import LeapLoginBody
from pylutron_leap.api.occupancy import (
    LeapMultiOccupancySensorBody,
    LeapOccupancySensorBody,
)
from pylutron_leap.api.ping import LeapPingBody
from pylutron_leap.api.processor import LeapMasterDeviceListBody
from pylutron_leap.api.version import LeapVersionBody
from pylutron_leap.api.zone import (
    LeapMultiZoneBody,
    LeapMultiZoneTypeGroupBody,
    LeapZoneBody,
    LeapZoneTypeGroupBody,
)

# from dataclasses import dataclassimport marshmallow_dataclass


logger = getLogger(__name__)

LeapModelledBodies = Union[
    LeapAreaDefinitionBody,
    LeapAreaStatusBody,
    LeapButtonStatusBody,
    LeapDeviceBody,
    LeapMasterDeviceListBody,
    LeapMultiAreaDefinitionBody,
    LeapMultiAreaStatusBody,
    LeapMultiDeviceBody,
    LeapMultiZoneBody,
    LeapMultiZoneTypeGroupBody,
    LeapZoneBody,
    LeapZoneTypeGroupBody,
]


@dataclass
class ResponseStatus:
    code: int
    message: str

    @classmethod
    def from_str(cls, data: str) -> "ResponseStatus":
        """Convert a str to a ResponseStatus."""
        space = data.find(" ")
        if space == -1:
            code = None
        else:
            try:
                code = int(data[:space])
                data = data[space + 1 :]
            except ValueError:
                code = None

        return ResponseStatus(code, data)  # type: ignore

    @post_dump
    def __render_status(self, data, many):
        if many:
            _result = [str(ResponseStatus(**x)) for x in data]
        else:
            _result = str(ResponseStatus(**data))
        return _result

    @pre_load
    def __parse_status(self, data, many, partial):
        if many:
            _result = [ResponseStatus.from_str(x).__dict__ for x in data]
        else:
            _result = ResponseStatus.from_str(data).__dict__
        return _result

    def is_successful(self) -> bool:
        """Check if the status code is in the range [200, 300)."""
        return self.code is not None and self.code >= 200 and self.code < 300

    def __str__(self) -> str:
        return f"{self.code} {self.message}"


@dataclass
class LeapDirectives:
    SuppressMessageBody: Optional[bool] = None


@marshmallow_dataclass.add_schema
@dataclass
class LeapMessageHeader:
    Url: str
    ClientTag: Optional[str] = None
    StatusCode: Optional[ResponseStatus] = None
    Directives: Optional[LeapDirectives] = None
    MessageBodyType: Optional[MessageBodyTypeEnum] = None

    def __repr__(self) -> str:
        return LeapMessageHeader.Schema().dumps(self)  # type: ignore

    @post_dump
    def remove_skip_values(self, data, many):
        def remove_nones(d):
            clean = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    nested = remove_nones(v)
                    if len(nested.keys()) > 0:
                        clean[k] = nested
                elif v is not None:
                    clean[k] = v
            return clean

        if many:
            _result = [remove_nones(x) for x in data]
        else:
            _result = remove_nones(data)

        return _result


@dataclass
class LeapExceptionBody:
    Message: str


@marshmallow_dataclass.add_schema
@dataclass
class LeapMessage:
    CommuniqueType: CommuniqueType
    Header: LeapMessageHeader
    Body: Optional[
        Union[
            LeapAreaStatusBody,
            LeapButtonBody,
            LeapButtonStatusBody,
            LeapCommandBody,
            LeapDeviceBody,
            LeapEmergencyBody,
            LeapExceptionBody,
            LeapLoadShedBody,
            LeapLoginBody,
            LeapMultiAreaDefinitionBody,
            LeapMultiAreaStatusBody,
            LeapMultiDeviceBody,
            LeapMultiDeviceDefinitionBody,
            LeapMultiEmergencyBody,
            LeapMultiOccupancySensorBody,
            LeapMultiZoneBody,
            LeapMultiZoneTypeGroupBody,
            LeapOccupancySensorBody,
            LeapPingBody,
            LeapVersionBody,
            LeapZoneBody,
            LeapZoneTypeGroupBody,
        ]
    ] = None

    @post_dump
    def remove_skip_values(self, data, many):
        def remove_nones(d):
            clean = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    nested = remove_nones(v)
                    if len(nested.keys()) > 0:
                        clean[k] = nested
                elif v is not None:
                    clean[k] = v
            return clean

        if many:
            _result = [remove_nones(x) for x in data]
        else:
            _result = remove_nones(data)

        return _result

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        _id = id_from_href(self.Header.Url or "")
        logger.debug(f"id from header: {_id}")
        if _id is not None:
            _ids.append(_id)

        related_ids = getattr(self.Body, "related_ids", None)
        if callable(related_ids):
            _ids.extend(cast(LeapModelledBodies, self.Body).related_ids())

        return _ids
