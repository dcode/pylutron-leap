from dataclasses import dataclass
from typing import Optional

from .enum import ContextTypeEnum


@dataclass
class LoginBody:
    ContextType: ContextTypeEnum
    href: Optional[str] = None
    LoginId: Optional[str] = None
    Password: Optional[str] = None


@dataclass
class LeapLoginBody:
    Login: LoginBody
