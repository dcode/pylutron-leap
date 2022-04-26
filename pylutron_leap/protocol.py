import logging
import sys
from asyncio import Future, Protocol, Transport

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class LeapProtocol(Protocol):
    transport: Transport = None
    completed: Future = None

    def connection_made(self, transport: Transport) -> None:
        self.transport = transport
        self.remote_addr = transport.get_extra_info("peername")
        logger.debug("connecting to {} port {}".format(*self.remote_addr))
        return super().connection_made(transport)

    def connection_lost(self, exc: Exception | None) -> None:

        self.transport.close()
        return super().connection_lost(exc)
