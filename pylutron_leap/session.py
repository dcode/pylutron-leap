import asyncio
import logging
import ssl
import sys
from functools import partial
from pathlib import Path
from typing import Awaitable, Callable, Dict, Iterable, List, Optional, Tuple, cast

from pylutron_leap.models import BaseModel
from pylutron_leap.models.messages import (
    get_all_area_subscribe,
    get_all_occupancy_subscribe,
    get_all_zone_subscribe,
    get_connected_processor,
    get_other_devices,
)

try:
    from asyncio import get_loop as get_loop  # type: ignore
except ImportError:
    # For Python 3.6 and earlier, we have to use get_event_loop instead
    from asyncio import get_event_loop as get_loop

from typing import Union

from pylutron_leap.api.enum import CommuniqueType, ContextTypeEnum, MessageBodyTypeEnum
from pylutron_leap.api.login import LoginBody
from pylutron_leap.api.message import LeapLoginBody, LeapMessage, LeapMessageHeader
from pylutron_leap.exception import SessionDisconnectedError
from pylutron_leap.leap import LeapProtocol, open_connection
from pylutron_leap.models.area import Area
from pylutron_leap.models.device import Device
from pylutron_leap.models.zone import Zone

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s (%(lineno)d): %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

PING_INTERVAL = 60.0
CONNECT_TIMEOUT = 5.0
REQUEST_TIMEOUT = 5.0
RECONNECT_DELAY = 2.0
LEAP_PORT = 8081


MessageCallback = Callable[[LeapMessage], Awaitable[None]]


class LeapSession(object):
    def __init__(
        self,
        host: str,
        port: int = LEAP_PORT,
        keyfile: Optional[Path] = None,
        certfile: Optional[Path] = None,
        ca_chain: Optional[Path] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_tls: Optional[bool] = False,
    ):
        self.config: Dict[str, Optional[str | int | bool | Path]] = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "verify_tls": verify_tls,
            "keyfile": keyfile,
            "certfile": certfile,
            "ca_chain": ca_chain,
        }

        self._login_task: Optional[asyncio.Task] = None
        # Use future so we can wait before the login starts and
        # don't need to wait for "login" on reconnect.
        self._login_completed: asyncio.Future = get_loop().create_future()
        self._leap: LeapProtocol
        self._monitor_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self.models: List[BaseModel] = []

    async def connect(self) -> None:
        if not self._login_completed.done():
            self._login_completed.cancel()
            self._login_completed = get_loop().create_future()

        self._monitor_task = get_loop().create_task(self._monitor())

        await self._login_completed

    @property
    def logged_in(self) -> bool:
        """Check if the bridge is connected and ready."""
        return (
            # are we connected?
            self._monitor_task is not None
            and not self._monitor_task.done()
            # are we ready?
            and self._login_completed.done()
            and not self._login_completed.cancelled()
            and self._login_completed.exception() is None
        )

    @property
    def current_leap_ids(self) -> Iterable[int]:
        return [x.leap_id for x in self.models]

    def is_connected(self) -> bool:
        """Will return True if currently connected to the Smart Bridge."""
        return self.logged_in

    @property
    def areas(self) -> Iterable[Area]:
        return cast(Iterable[Area], filter(lambda x: isinstance(x, Area), self.models))

    @property
    def devices(self) -> Iterable[Device]:
        return cast(
            Iterable[Device], filter(lambda x: isinstance(x, Device), self.models)
        )

    @property
    def zones(self) -> Iterable[Zone]:
        return cast(Iterable[Zone], filter(lambda x: isinstance(x, Zone), self.models))

    async def request(self, message: LeapMessage) -> LeapMessage:
        if not self.logged_in:
            await self.connect()
        _response = await self._leap.request(message)
        return _response

    async def subscribe(
        self, message: LeapMessage, callback: MessageCallback
    ) -> Tuple[LeapMessage, str]:
        if not self.logged_in:
            await self.connect()

        logger.debug("Subscribing from session")
        return await self._leap.subscribe(message, callback)

    async def session_info(self) -> None:
        """
        Get current privilege level and configured LEAP version
        TODO: Allow setting LEAP version
        """
        _msg = LeapMessage(  # type: ignore
            CommuniqueType=CommuniqueType.ReadRequest,
            Header=LeapMessageHeader(  # type: ignore
                Url="/clientsetting",
            ),
        )
        logger.debug(f"Requesting Session Info: {_msg}")
        _response = await self._leap.request(_msg)
        logger.debug(f"Session Info response: {_response}")

    async def _connect(self):
        # TODO: Make context options configurable maybe
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True

        if self.config["verify_tls"] is False:
            ssl_context.verify_mode = ssl.CERT_NONE
            ssl_context.check_hostname = False

        if self.config.get("ca_chain", None):
            ssl_context.load_verify_locations(self.config["ca_chain"])
            ssl_context.verify_mode = ssl.CERT_REQUIRED

        if self.config.get("keyfile", None) or self.config.get("certfile", None):
            if not (
                self.config.get("keyfile", None) and self.config.get("certfile", None)
            ):
                logger.error("Both keyfile and certfile are required for TLS auth!")
                raise ValueError("Both keyfile and certfile are required for TLS auth!")
            else:
                ssl_context.load_cert_chain(
                    self.config["certfile"], self.config["keyfile"]
                )

        self._leap = await open_connection(
            host=self.config["host"],
            port=self.config["port"],
            server_hostname="",
            ssl=ssl_context,
        )

    async def _login(self):
        _msg = LeapMessage(
            CommuniqueType=CommuniqueType.UpdateRequest,
            Header=LeapMessageHeader(
                MessageBodyType=MessageBodyTypeEnum.OneLoginDefinition, Url="/login"
            ),
            Body=LeapLoginBody(
                Login=LoginBody(
                    ContextType=ContextTypeEnum.Application,
                    LoginId=self.config["username"],
                    Password=self.config["password"],
                )
            ),
        )

        logger.debug(f"Logging in. {_msg}")
        _response = await self._leap.request(_msg)
        logger.debug(f"Login response: {_response}")

        if not self._login_completed.done():
            self._login_completed.set_result(None)

    async def _initialize(self) -> None:
        """Do some initial setup to enumerate the system state and subscribe to events"""

        logger.debug("Waiting for _login_completed before initilization")
        await self._login_completed

        # Subscribe to all zones
        logger.debug("Subscribing to all zones")
        _msg = get_all_zone_subscribe()
        response, sub_tag = await self.subscribe(
            _msg, partial(handle_response_session, self)
        )
        self.zone_subscription_tag = sub_tag
        await self.handle_response(response)

        # Subscribe to all areas
        logger.debug("Subscribing to all areas")
        _msg = get_all_area_subscribe()
        response, sub_tag = await self.subscribe(
            _msg, partial(handle_response_session, self)
        )

        self.area_subscription_tag = sub_tag
        await self.handle_response(response)
        logger.debug("Subscribed to areas")

        # TODO: Once all areas have been populated, need to:
        #  - get area definition: `/area/XXX`
        #  - enumerate zones for each area:  `/area/XXX/associatedzone`

        # Subscribe to occupancygroup status events
        _msg = get_all_occupancy_subscribe()
        _resp, sub_tag = await self.subscribe(
            _msg, partial(handle_response_session, self)
        )

        # Enumerate Devices
        # TODO: Implement "associated-object" lookups
        logger.debug("Query processor information")
        _msg = get_connected_processor()
        response = await self._leap.request(_msg)
        await self.handle_response(response)

        logger.debug("Query other devices")
        _msg = get_other_devices()
        response = await self._leap.request(_msg)
        await self.handle_response(response)

        # Handle unsolicited messages
        logger.debug("Subscribing to everything else")
        self._leap.subscribe_unsolicited(partial(handle_response_session, self))

        if not self._initialize_task.done():
            self._initialize_task.set_result(None)

    async def _monitor(self):
        """Event monitoring loop."""
        try:
            while True:
                await self._monitor_once()
        except asyncio.CancelledError:
            pass
        except Exception as ex:
            logger.critical("monitor loop has exited", exc_info=1)
            if not self._login_completed.done():
                self._login_completed.set_exception(ex)
            raise
        finally:
            self._login_completed.cancel()

    async def _monitor_once(self):
        """Monitor for events until an error occurs."""
        try:
            logger.debug("Connecting to Smart Bridge via SSL")
            await self._connect()
            logger.debug("Successfully connected to Smart Bridge.")

            if self._login_task is not None:
                self._login_task.cancel()

            if self._ping_task is not None:
                self._ping_task.cancel()

            self._login_task = get_loop().create_task(self._login())
            self._ping_task = get_loop().create_task(self._ping())
            self._initialize_task = get_loop().create_task(self._initialize())

            get_loop().create_task(self.session_info())
            await self._leap.run()

            logger.warning("LEAP session ended. Reconnecting...")
            await asyncio.sleep(RECONNECT_DELAY)
        # ignore OSError too.
        # sometimes you get OSError instead of ConnectionError.
        except (
            ValueError,
            ConnectionError,
            OSError,
            asyncio.TimeoutError,
            SessionDisconnectedError,
        ):
            logger.warning("Reconnecting...", exc_info=1)
            await asyncio.sleep(RECONNECT_DELAY)
        finally:
            if self._initialize_task is not None:
                self._initialize_task.cancel()
                self._initialize_task = None

            if self._login_task is not None:
                self._login_task.cancel()
                self._login_task = None

            if self._ping_task is not None:
                self._ping_task.cancel()
                self._ping_task = None

            if self._leap is not None:
                self._leap.close()
                self._leap = None

    async def _ping(self):
        """Periodically ping the LEAP server to keep the connection open."""
        try:
            while True:
                await asyncio.sleep(PING_INTERVAL)
                _msg = LeapMessage(
                    CommuniqueType.ReadRequest,
                    LeapMessageHeader(Url="/server/status/ping"),
                )
                logger.debug(f"Pinging server: {_msg}")
                _resp = await self._leap.request(_msg)
                logger.debug(f"Ping response: {_resp}")

        except asyncio.TimeoutError:
            logger.warning("ping was not answered. closing connection.")
            self._leap.close()
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.warning("ping failed. closing connection.", exc_info=1)
            self._leap.close()
            raise

    async def handle_response(self, response: LeapMessage) -> None:
        logger.debug("Handling message: ")
        logger.debug(LeapMessage.Schema().dump(response))  # type: ignore

        _related_ids: list[int] = []

        if response is not None:
            related_ids = getattr(response, "related_ids", None)
            if callable(related_ids):
                _related_ids = response.related_ids()

        logger.debug(f"Related IDs: {_related_ids}")

        if Area.can_handle_response(response):
            Area.handle_response(self, response)
        elif Device.can_handle_response(response):
            Device.handle_response(self, response)
        elif Zone.can_handle_response(response):
            Zone.handle_response(self, response)

    def close(self):
        self.leap.close()


async def handle_response_session(session: LeapSession, response: LeapMessage) -> None:
    await session.handle_response(response)
