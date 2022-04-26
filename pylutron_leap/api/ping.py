from dataclasses import dataclass


@dataclass
class PingResponseType:
    LEAPVersion: float


@dataclass
class LeapPingBody:
    PingResponse: PingResponseType
