from dataclasses import dataclass

from .enum import ButtonEventState, ButtonEventType


@dataclass
class ButtonCommandType:
    CommandType: ButtonEventState


@dataclass
class ButtonEvent:
    EventType: ButtonEventType


@dataclass
class ButtonStatus:
    ButtonEvent: ButtonEvent


@dataclass
class LeapButtonStatusBody:
    ButtonStatus: ButtonStatus

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        return _ids


@dataclass
class LeapButtonBody:
    Command: ButtonCommandType

    def related_ids(self) -> list[int]:
        _ids: list[int] = []
        return _ids
