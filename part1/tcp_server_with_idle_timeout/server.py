import select
import socket
import traceback
from collections.abc import Iterator

from .interface import TCPHandlerI, TCPServerI


class TCPServer(TCPServerI):
    def __init__(
        self,
        host: str,
        port: int,
        handler: TCPHandlerI,
        client_idle_timeout: float = 5,
    ):
        self.address = (host, port)
        self.server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.address)

        self.client_idle_timeout = client_idle_timeout

        self.handler = handler

    def serve_forever(self):
        """Основной цикл сервера: опрашиваем сокет, принимаем и обрабатываем клиентов."""
        self.server_socket.listen()
        print(f"Python: сервер запущен на прослушивание {self.address[0]}:{self.address[1]}")

        with self.server_socket as server_socket:
            while True:
                client_socket, addr = server_socket.accept()
                self._handle_request(client_socket, addr)

    def _handle_request(self, client_socket: socket.socket, addr):
        """
        Обработчик клиентского соединения.
        """
        print(f"Python: обрабатываю запрос клиента {addr}")
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
        client_data = self.read_client_data(client_socket)
        processed_data = self.handler.handle(client_data)
        self.send_to_client(client_socket, processed_data)

    def shutdown_request(self, client_socket: socket.socket):
        """Закрытие соединения с клиентом, отправка FIN."""
        try:
            client_socket.shutdown(socket.SHUT_WR)
            print("Python: отправил (FIN) клиенту")
        except OSError:
            # Если клиент уже закрыл соединение
            pass
        client_socket.close()
        print("Python: закрыл соединение с клиентом")

    def read_client_data(self, client_socket: socket.socket) -> Iterator[bytes]:
        """Чтение данных клиента."""

        while True:
            ready, _, _ = select.select(
                [client_socket],
                [],
                [],
                self.client_idle_timeout,
            )
            if ready:
                chunk = client_socket.recv(1024)
            else:
                print("Python: timeout ожидания клиента.")
                break

            if chunk:
                yield chunk
            else:
                print("Python: клиент прислал (FIN).")
                break

    def send_to_client(self, client_socket: socket.socket, data: Iterator[bytes]):
        """Отправляет данные клиенту."""
        print("Python: отправляю ответ клиенту")
        for chunk in data:
            try:
                client_socket.sendall(chunk)
            except OSError:
                print("Python: клиент закрыл соединение до получения данных")

    def handle_error(self, client_socket, addr):
        """Обработка ошибок во время выполнения запроса."""
        print(f"Python: произошла ошибка во время обработки запроса клиента {addr}")
        traceback.print_exc()


class TCPEchoHandler(TCPHandlerI):
    def handle(self, data: Iterator[bytes]) -> Iterator[bytes]:
        return data


if __name__ == "__main__":
    server = TCPServer("0.0.0.0", 9999, TCPEchoHandler())
    server.serve_forever()
