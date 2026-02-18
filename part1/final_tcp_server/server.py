import logging
import select
import signal
import socket
import traceback
from collections.abc import Iterator
from threading import Event

from .interface import TCPHandlerI, TCPServerI
from .socket_io import SocketIO


class TCPServer(TCPServerI):
    def __init__(
        self,
        host: str,
        port: int,
        handler: TCPHandlerI,
        poll_interval: float = 0.5,
        client_idle_timeout: float = 5,
        shutdown_timeout: float = 10,
    ):
        self.address = (host, port)
        self.server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.address)

        self.poll_interval = poll_interval
        self.client_idle_timeout = client_idle_timeout
        self.shutdown_timeout = shutdown_timeout
        self.handler = handler

        self.shutdown_event = Event()
        signal.signal(signal.SIGTERM, self._on_shutdown)
        signal.signal(signal.SIGINT, self._on_shutdown)

    def _on_shutdown(self, signum, _):
        """Сигнальный обработчик - выставляет флаг завершения."""
        logging.warning("Python: получен сигнал завершения")
        logging.warning("Python: после обработки всех активных запросов сервер будет остановлен")
        self.shutdown_event.set()

    def serve_forever(self):
        """Основной цикл сервера: опрашиваем сокет, принимаем и обрабатываем клиентов."""
        self.server_socket.listen()
        logging.info(f"Python: сервер запущен на прослушивание {self.address[0]}:{self.address[1]}")
        self.shutdown_event.clear()

        with self.server_socket as server_socket:
            while not self.shutdown_event.is_set():
                ready, _, _ = select.select(
                    [server_socket],
                    [],
                    [],
                    self.poll_interval,
                )
                if ready:
                    client_socket, addr = server_socket.accept()
                    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    self._handle_request(client_socket, addr)

    def _handle_request(self, client_socket: socket.socket, addr):
        """
        Обработчик клиентского соединения.
        """
        logging.debug(f"Python: обрабатываю запрос клиента {addr}")
        try:
            self._process_request(client_socket)
        except Exception:
            self.handle_error(client_socket, addr)
        finally:
            self.shutdown_request(client_socket)

    def _process_request(self, client_socket: socket.socket):
        """
        Читает данные клиента и вызывает бизнес-логику из self.handler.
        """
        socket_io = SocketIO(
            socket=client_socket,
            shutdown_event=self.shutdown_event,
            poll_interval=self.poll_interval,
            idle_timeout=self.client_idle_timeout,
            shutdown_timeout=self.shutdown_timeout,
        )
        processed_data = self.handler.handle(socket_io)
        self.send_to_client(client_socket, processed_data)

    def shutdown_request(self, client_socket: socket.socket):
        """Закрытие соединения с клиентом, отправка FIN."""
        try:
            client_socket.shutdown(socket.SHUT_WR)
            logging.debug("Python: отправил (FIN) клиенту")
        except OSError:
            # Если клиент уже закрыл соединение
            pass
        client_socket.close()
        logging.debug("Python: закрыл соединение с клиентом")

    def send_to_client(self, client_socket: socket.socket, data: Iterator[bytes]):
        """Отправляет данные клиенту."""
        logging.debug("Python: отправляю ответ клиенту")
        for chunk in data:
            try:
                client_socket.sendall(chunk)
            except OSError:
                logging.debug("Python: клиент закрыл соединение до получения данных")

    def handle_error(self, client_socket, addr):
        """Обработка ошибок во время выполнения запроса."""
        logging.error(f"Python: произошла ошибка во время обработки запроса клиента {addr}")
        traceback.print_exc()


class TCPEchoHandler(TCPHandlerI):
    def handle(self, data: SocketIO) -> Iterator[bytes]:
        return data


if __name__ == "__main__":
    server = TCPServer("0.0.0.0", 9999, TCPEchoHandler())
    server.serve_forever()
