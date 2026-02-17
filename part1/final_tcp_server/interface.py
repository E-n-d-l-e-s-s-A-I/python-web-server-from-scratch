from collections.abc import Iterator
from typing import Protocol

from .socket_io import SocketIO


class TCPHandlerI(Protocol):
    def handle(self, data: SocketIO) -> Iterator[bytes]:
        raise NotImplementedError()


class TCPServerI(Protocol):
    def __init__(
        self,
        host: str,
        port: int,
        handler: TCPHandlerI,
    ):
        raise NotImplementedError()

    def serve_forever(self):
        """Запуск сервера."""
        raise NotImplementedError()
