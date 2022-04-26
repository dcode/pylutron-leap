from collections.abc import Sequence
from logging import getLogger
from typing import List, Optional

from pylutron_leap.api import id_from_href
from pylutron_leap.api.command import LeapCommand, LeapCommandBody
from pylutron_leap.api.enum import CommandType, CommuniqueType, MessageBodyTypeEnum
from pylutron_leap.api.message import LeapMessage, LeapMessageHeader
from pylutron_leap.models import BaseModel
from pylutron_leap.session import LeapSession

logger = getLogger(__name__)


class ProcessorModel(BaseModel):
    def __init__(self, leap_id: int, session: LeapSession = None):
        super().__init__(leap_id, session)

        self.serial: Optional[int] = None
        self.mac_addr: Optional[str] = None
        self.proc_id: Optional[int] = None

    @classmethod
    async def get_processors(cls, session) -> Sequence["ProcessorModel"]:
        _processors: List[ProcessorModel] = list()

        _msg = LeapMessage(
            CommuniqueType=CommuniqueType.CreateRequest,
            Header=LeapMessageHeader(Url="/project/masterdevicelist"),
        )
        _response = await session.request(_msg)

        if (
            _response.Header.MessageBodyType
            != MessageBodyTypeEnum.OneMasterDeviceListDefinition
        ):
            return _processors

        for entry in _response.Body.MasterDeviceList.Devices:
            _id = id_from_href(entry.href)
            if _id is not None:
                _proc = ProcessorModel(_id, session)

                _proc.serial = entry.SerialNumber
                _proc.mac_addr = ",".join(
                    [x.MACAddress for x in entry.NetworkInterfaces]
                )
                _proc.proc_id = entry.IPL.ProcessorID

                _processors.append(_proc)

        return _processors

    async def reboot(self):
        _msg = LeapMessage(
            CommuniqueType=CommuniqueType.CreateRequest,
            Header=LeapMessageHeader(Url=f"/device/{self.leap_id}/commandprocessor"),
            Body=LeapCommandBody(Command=LeapCommand(CommandType=CommandType.Reboot)),
        )

        # Expect {"CommuniqueType":"CreateResponse","Header":{"StatusCode":"204 NoContent","Url":"/device/128/commandprocessor"}}

        _response = await self.session.request(_msg)

        await self.handle_state(_response)
