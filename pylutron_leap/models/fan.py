from logging import getLogger

from pylutron_leap.api import id_from_href
from pylutron_leap.api.command import LeapCommand, LeapCommandBody
from pylutron_leap.api.enum import (
    CommandType,
    CommuniqueType,
    FanSpeedType,
    MessageBodyTypeEnum,
)
from pylutron_leap.api.message import LeapMessage, LeapMessageHeader
from pylutron_leap.api.parameters import FanSpeedParametersType
from pylutron_leap.api.zone import ZoneStatusType
from pylutron_leap.models.zone import Zone
from pylutron_leap.session import LeapSession

logger = getLogger(__name__)


class FanModel(Zone):
    def __init__(self, leap_id: int, session: LeapSession = None):
        super().__init__(leap_id, session)
        self.fan_speed = FanSpeedType.Unknown

    async def handle_state(self, response: LeapMessage) -> None:
        if response.Header.MessageBodyType == MessageBodyTypeEnum.OneZoneStatus:
            try:
                _id = id_from_href(response.Body.ZoneStatus.href)
            except ValueError as exc:
                logger.error(exc)
                logger.error(f"Unable to determine zone id from response: {response}")
                return

            if self.leap_id == _id:
                await self.update_state(response.Body.ZoneStatus)

        elif response.Header.MessageBodyType == MessageBodyTypeEnum.MultipleZoneStatus:
            if response.Body.ZoneStatuses is not None:
                for entry in response.Body.ZoneStatuses:
                    try:
                        _id = id_from_href(response.Body.ZoneStatus.href)
                    except ValueError as exc:
                        logger.error(exc)
                        logger.error(f"Unable to determine zone id from entry: {entry}")
                        continue

                    if self.leap_id == _id:
                        await self.update_state(response.Body.ZoneStatus)

    async def update_state(self, status: ZoneStatusType):
        if status.FanSpeed is not None:
            self.fan_speed = status.FanSpeed

    async def set_speed(self, speed: FanSpeedType):

        _msg = LeapMessage(
            CommuniqueType=CommuniqueType.CreateRequest,
            Header=LeapMessageHeader(Url=f"/zone/{self.leap_id}/commandprocessor"),
            Body=LeapCommandBody(
                Command=LeapCommand(
                    CommandType=CommandType.GoToFanSpeed,
                    FanSpeedParameters=FanSpeedParametersType(FanSpeed=speed),
                )
            ),
        )

        _response = await self.session.request(_msg)

        await self.handle_state(_response)

    # TODO: possibly make speed a property and cache the get lookup
    async def get_speed(self) -> FanSpeedType:
        _msg = LeapMessage(
            CommuniqueType=CommuniqueType.ReadRequest,
            Header=LeapMessageHeader(Url=f"/zone/{self.leap_id}/status"),
        )

        _response = await self.session.request(_msg)

        await self.handle_state(_response)

        return self.fan_speed
