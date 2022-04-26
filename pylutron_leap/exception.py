from typing import Optional

from pylutron_leap.api.message import LeapMessage, ResponseStatus


class SessionDisconnectedError(Exception):
    """Raised when the connection is lost while waiting for a response."""

    pass


class SessionResponseError(Exception):
    """Raised when the bridge sends an error response."""

    def __init__(self, response: LeapMessage):
        """Create a BridgeResponseError."""
        super().__init__(str(response.Header.StatusCode))
        self.response = response

    @property
    def code(self) -> Optional[ResponseStatus]:
        """Get the status code returned by the server."""
        return self.response.Header.StatusCode
