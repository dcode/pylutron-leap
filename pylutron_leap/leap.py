"""LEAP protocol layer."""

import asyncio
import json
import logging
import uuid
from typing import Awaitable, Callable, Dict, List, Tuple

from pylutron_leap.api.enum import CommuniqueType
from pylutron_leap.api.message import LeapMessage
from pylutron_leap.exception import SessionDisconnectedError

logger = logging.getLogger(__name__)
_DEFAULT_LIMIT = 2**16


def _make_tag() -> str:
    return str(uuid.uuid4())


MessageCallback = Callable[[LeapMessage], Awaitable[None]]


class LeapProtocol:
    """A wrapper for making LEAP calls."""

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        """Wrap a reader and writer with a LEAP request and response protocol."""
        self._reader = reader
        self._writer = writer
        self._in_flight_requests: Dict[str, "asyncio.Future[LeapMessage]"] = {}
        self._tagged_subscriptions: Dict[str, MessageCallback] = {}
        self._unsolicited_subs: List[MessageCallback] = []

    async def request(self, message: LeapMessage) -> LeapMessage:
        """Make a request to the bridge and return the response."""
        if message.Header.ClientTag is None:
            _tag = _make_tag()
            message.Header.ClientTag = _tag
        else:
            _tag = message.Header.ClientTag

        _future: asyncio.Future = asyncio.get_running_loop().create_future()
        _msg_dict = LeapMessage.Schema().dump(message)  # type: ignore

        self._in_flight_requests[_tag] = _future

        # remove cancelled tasks
        def clean_up(future):
            if future.cancelled():
                self._in_flight_requests.pop(_tag, None)

        _future.add_done_callback(clean_up)

        try:
            _text = json.dumps(_msg_dict).encode("UTF-8")
            logger.debug(f"Sending {_text!r}")
            self._writer.write(_text + b"\r\n")

            return await _future
        finally:
            self._in_flight_requests.pop(_tag, None)

    async def run(self):
        """Event monitoring loop."""
        logger.debug("Entering run() loop")
        while not self._reader.at_eof():
            _received: bytes = await self._reader.readline()
            logger.debug(f"Received raw bytes: {_received.decode('UTF-8') }")

            if _received == b"":
                break

            _resp_dict: Dict[str, str | Dict] = json.loads(_received.decode("UTF-8"))

            if isinstance(_resp_dict, dict):
                msg: LeapMessage = LeapMessage.Schema().load(_resp_dict)
                tag = msg.Header.ClientTag
                if tag is not None:
                    in_flight = self._in_flight_requests.pop(tag, None)
                    if in_flight is not None and not in_flight.done():
                        logger.debug("received: %s", msg)
                        in_flight.set_result(msg)
                    else:
                        subscription = self._tagged_subscriptions.get(tag, None)
                        if subscription is not None:
                            logger.debug(f"received for subscription {tag}: {msg}")
                            logger.debug(f"Calling {subscription}")
                            await subscription(msg)
                        else:
                            logger.error(
                                f"Was not expecting message with tag {tag}: {msg}"
                            )
                else:
                    logger.debug("Received message with no tag: %s", msg)
                    for handler in self._unsolicited_subs:
                        try:
                            await handler(msg)
                        except Exception:  # pylint: disable=broad-except
                            logger.exception(
                                "Got exception from unsolicited message handler"
                            )

    async def subscribe(
        self, msg: LeapMessage, callback: MessageCallback
    ) -> Tuple[LeapMessage, str]:
        """
        Subscribe to events from the bridge.

        This is similar to a normal request, except that the bridge is expected to send
        additional responses with the same tag value at a later time. These additional
        responses will be handled by the provided callback.

        This returns both the response message and a string that will be required for
        unsubscribing (not implemented).
        """
        if not callable(callback):
            raise TypeError("callback must be callable")

        if not msg.CommuniqueType == CommuniqueType.SubscribeRequest:
            raise TypeError("CommuniqueType must be SubscribeRequest")

        if msg.Header.ClientTag is None:
            tag = _make_tag()
            msg.Header.ClientTag = tag

        _resp: LeapMessage = await self.request(msg)

        status = _resp.Header.StatusCode
        if status is not None and status.is_successful():
            self._tagged_subscriptions[tag] = callback
            logger.debug(f"Subscribed to {msg.Header.Url} as {tag}")
        else:
            logger.error(f"Subscription to {msg.Header.Url} failed.")

        return (_resp, tag)

    def subscribe_unsolicited(self, callback: MessageCallback):
        """
        Subscribe to notifications of unsolicited events.

        The provided callback will be executed when the bridge sends an untagged
        LeapMessage.
        """
        if not callable(callback):
            raise TypeError("callback must be callable")
        self._unsolicited_subs.append(callback)

    def unsubscribe_unsolicited(self, callback: MessageCallback):
        """Unsubscribe from notifications of unsolicited events."""
        self._unsolicited_subs.remove(callback)

    def close(self):
        """Disconnect."""
        self._writer.close()

        for request in self._in_flight_requests.values():
            request.set_exception(SessionDisconnectedError())
        self._in_flight_requests.clear()
        self._tagged_subscriptions.clear()


async def open_connection(
    host: str, port: int, *, limit: int = _DEFAULT_LIMIT, **kwds
) -> LeapProtocol:
    """Open a stream and wrap it with LEAP."""
    logger.debug(f"Connecting to {host}:{port}")
    reader, writer = await asyncio.open_connection(host, port, limit=limit, **kwds)

    _peer = writer.transport.get_extra_info("peername")
    _cipher = writer.transport.get_extra_info("cipher")
    logger.debug(f"Connected to {_peer} using {_cipher}")

    return LeapProtocol(reader, writer)
