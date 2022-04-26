from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence

from pylutron_leap.api.message import LeapMessage

if TYPE_CHECKING:
    from pylutron_leap.session import LeapSession


class BaseModel(object):
    """
    This class aims to provide common structure to all models. The models
    represent "thing" within the protocol that can be interacted with.

    Attributes:
        default_session   Session used send commands. May be overriden on
                          a per-model basis.
    """

    default_session: LeapSession

    def __init__(self, leap_id: int, session: Optional[LeapSession] = None):
        self.leap_id: int = leap_id
        self.session: LeapSession

        if session is not None:
            self.session = session
        else:
            self.session = self.default_session

    @classmethod
    def can_handle_response(cls, response: LeapMessage) -> bool:
        return False

    @classmethod
    def handle_response(
        cls, session: LeapSession, response: LeapMessage
    ) -> Sequence[BaseModel]:
        raise NotImplementedError(
            "handle_response() should be implemented in derived models"
        )


# """
# These types have unique IDs and may be represented by a Python model class
# """
# ModelBodyTypes = Union[
#     LeapAreaStatusBody,
#     LeapButtonBody,
#     LeapButtonStatusBody,
#     LeapCommandBody,
#     LeapDeviceBody,
#     LeapEmergencyBody,
#     LeapExceptionBody,
#     LeapLoadShedBody,
#     LeapLoginBody,
#     LeapMasterDeviceListBody,
#     LeapMultiAreaDefinitionBody,
#     LeapMultiAreaStatusBody,
#     LeapMultiDeviceBody,
#     LeapMultiEmergencyBody,
#     LeapMultiOccupancySensorBody,
#     LeapMultiZoneBody,
#     LeapMultiZoneTypeGroupBody,
#     LeapOccupancySensorBody,
#     LeapPingBody,
#     LeapVersionBody,
#     LeapZoneBody,
#     LeapZoneTypeGroupBody,
# ]
