import re
from dataclasses import dataclass


@dataclass
class HRef:
    href: str


_HREFRE = re.compile(r"/(?:\D+)/(\d+)(?:\/\D+)?")


def id_from_href(href: str) -> int | None:
    """Get an id from any kind of href.

    Retrurns None if id cannot be determined from the format
    """
    match = _HREFRE.match(href)

    if match is None:
        return None

    return int(match.group(1))
