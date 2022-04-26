from __future__ import annotations

from collections.abc import Coroutine
from logging import getLogger
from typing import TYPE_CHECKING, List, Optional, Sequence, cast

from pylutron_leap.api import HRef, id_from_href
from pylutron_leap.api.enum import FanSpeedType, MessageBodyTypeEnum, SwitchedState
from pylutron_leap.api.message import LeapMessage, LeapMultiZoneBody, LeapZoneBody
from pylutron_leap.api.zone import (
    CCOZoneLevel,
    ColorTuningStatusType,
    LeapMultipleZoneExpandedStatusBody,
    RecepticalState,
    ZoneCategoryType,
    ZoneDefinitionType,
    ZonePhaseSettings,
    ZoneStatusType,
    ZoneTuningSettings,
    ZoneType,
)
from pylutron_leap.models import BaseModel
from pylutron_leap.models.device import Device

logger = getLogger(__name__)

if TYPE_CHECKING:
    from pylutron_leap.session import LeapSession

ZoneBodyTypes = [
    MessageBodyTypeEnum.OneZoneDefinition,
    MessageBodyTypeEnum.OneZoneStatus,
    MessageBodyTypeEnum.OneZoneTypeGroupStatus,
    MessageBodyTypeEnum.MultipleZoneDefinition,
    MessageBodyTypeEnum.MultipleZoneStatus,
    MessageBodyTypeEnum.MultipleZoneTypeGroupStatus,
]


class Zone(BaseModel):
    instances: Sequence[Zone] = []
    default_session: LeapSession
    subscribe_callbacks: Sequence[Coroutine[None, LeapMessage, None]] = []

    def __init__(self, leap_id: int, session: LeapSession = None):
        super().__init__(leap_id, session)

        # Zone definition fields
        self.associated_area: Optional[HRef] = None
        self.associated_facade: Optional[HRef] = None
        self.category: Optional[ZoneCategoryType] = None
        self.color_tuning_properties: Optional[ColorTuningStatusType] = None
        self.control_type: Optional[ZoneType] = None
        self.device: Optional[Device] = None
        self.name: Optional[str] = None
        self.phase_settings: Optional[ZonePhaseSettings] = None
        self.sort_order: Optional[int] = None
        self.tuning_settings: Optional[ZoneTuningSettings] = None

        # Zone status fields
        self.availability: Optional[str] = None
        self.cco_level: Optional[CCOZoneLevel] = None
        self.color_tuning_status: Optional[ColorTuningStatusType] = None
        self.fan_speed: Optional[FanSpeedType] = None
        self.level: Optional[int] = None
        self.receptacle_level: Optional[RecepticalState] = None
        self.status_accuracy: Optional[str] = None
        self.switched_level: Optional[SwitchedState] = None
        self.tilt: Optional[int] = None
        self.vibrancy: Optional[int] = None

    @classmethod
    def can_handle_response(cls, response: LeapMessage) -> bool:
        return response.Header.MessageBodyType in ZoneBodyTypes

    def _update_status(self, status: ZoneStatusType) -> None:

        if status.SwitchedLevel is not None:
            self.switched_level = status.SwitchedLevel

        if status.Level is not None:
            self.level = status.Level

        if status.Tilt is not None:
            self.tilt = status.Tilt

        if status.Vibrancy is not None:
            self.vibrancy = status.Vibrancy

        if status.ColorTuningStatus is not None:
            self.color_tuning_status = status.ColorTuningStatus

        if status.CCOLevel is not None:
            self.cco_level = status.CCOLevel

        if status.ReceptacleLevel is not None:
            self.receptacle_level = status.ReceptacleLevel

        if status.FanSpeed is not None:
            self.fan_speed = status.FanSpeed

        if status.StatusAccuracy is not None:
            self.status_accuracy = status.StatusAccuracy

        if status.Availability is not None:
            self.availability = status.Availability

    def _update_definition(self, defn: ZoneDefinitionType) -> None:

        if defn.Name is not None:
            self.name = defn.Name

        if defn.SortOrder is not None:
            self.sort_order = defn.SortOrder

        if defn.ControlType is not None:
            self.control_type = defn.ControlType

        if defn.Category is not None:
            self.category = defn.Category

        if defn.Device is not None:
            _id = id_from_href(defn.Device.href)
            if _id is not None:
                self.device = Device.get_or_create_device(self.session, _id)

        if defn.ColorTuningProperties is not None:
            self.color_tuning_properties = defn.ColorTuningProperties

        if defn.PhaseSettings is not None:
            self.phase_settings = defn.PhaseSettings

        if defn.TuningSettings is not None:
            self.tuning_settings = defn.TuningSettings

        if defn.AssociatedArea is not None:
            self.associated_area = defn.AssociatedArea

        if defn.AssociatedFacade is not None:
            self.associated_facade = defn.AssociatedFacade

    @classmethod
    def get_or_create_zone(cls, session: LeapSession, leap_id: int) -> Zone:
        _zones = list(filter(lambda x: x.leap_id == leap_id, session.zones))
        if len(_zones):
            assert len(_zones) == 1
            return _zones[0]
        else:
            _zone = Zone(leap_id, session)
            session.models.append(_zone)
            return _zone

    @property
    def href(self) -> str:
        return f"/zone/{self.leap_id}"

    @classmethod
    def handle_response(
        cls, session: LeapSession, response: LeapMessage
    ) -> Sequence[Zone]:

        _ids: list[int]
        _zone: Zone
        entry: ZoneStatusType | ZoneDefinitionType

        _updated_zones: List[Zone] = []

        if response.Header.MessageBodyType == MessageBodyTypeEnum.OneZoneStatus:

            _ids = response.related_ids()
            assert len(_ids) == 1

            _zone = cls.get_or_create_zone(session, _ids[0])
            _zone._update_status(cast(LeapZoneBody, response.Body).ZoneStatus)

            _updated_zones.append(_zone)

        elif response.Header.MessageBodyType == MessageBodyTypeEnum.MultipleZoneStatus:
            for entry in cast(LeapMultiZoneBody, response.Body).ZoneStatuses:
                _ids = entry.related_ids()
                if len(_ids) == 0:
                    logger.error("Protocol error! No zone status bodies found")
                    return _updated_zones

                _zone = cls.get_or_create_zone(session, _ids[0])
                _zone._update_status(entry)

                _updated_zones.append(_zone)

        elif (
            response.Header.MessageBodyType
            == MessageBodyTypeEnum.MultipleZoneExpandedStatus
        ):
            for entry in cast(
                LeapMultipleZoneExpandedStatusBody, response.Body
            ).ZoneExpandedStatuses:
                _ids = entry.related_ids()
                if len(_ids) == 0:
                    logger.error("Protocol error! No zone expanded status bodies found")
                    return _updated_zones

                _zone = cls.get_or_create_zone(session, _ids[0])
                _zone._update_status(entry)
                if getattr(entry, "Zone") is not None:
                    _defn: ZoneDefinitionType = cast(ZoneDefinitionType, entry.Zone)
                    _zone._update_definition(_defn)

                _updated_zones.append(_zone)

        return _updated_zones
