from dataclasses import dataclass
from typing import Optional

from .enum import SessionPermissions


@dataclass
class PermissionsType:
    SessionRole: SessionPermissions


@dataclass
class VersionBody:
    href: Optional[str]
    ClientMajorVersion: Optional[int]
    ClientMinorVersion: Optional[int]
    Permissions: Optional[PermissionsType]


@dataclass
class LeapVersionBody:
    ClientSetting: VersionBody
