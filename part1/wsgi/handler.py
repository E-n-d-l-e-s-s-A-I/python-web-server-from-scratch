import io
from collections.abc import Iterator
from dataclasses import dataclass

from final_tcp_server.interface import TCPHandlerI
from final_tcp_server.socket_io import SocketIO


@dataclass
class HTTPRequest:
    method: str
    path: str
    protocol: str
    headers: dict[str, str]
    body: io.BytesIO


class WSGIHandler(TCPHandlerI):
    def __init__(self, app, host: str, port: int):
        self.app = app
        self.port = port
        self.host = host

    def handle(self, data: SocketIO) -> Iterator[bytes]:
        try:
            http_request = self._parse_http_request(data)
        except Exception:
            status, headers_list = "400 Bad Request", [("Content-Type", "text/plain")]
            body_iterator = [b"400 Bad Request"]
            return self._generate_http_response(status, headers_list, body_iterator)

        environ = self._generate_environ(http_request)
        response_headers = []

        def start_response(status, headers_list):
            response_headers.extend([status, headers_list])

        # Вызываем WSGI-приложение
        try:
            body_iterator = self.app(environ, start_response)
            status, headers_list = response_headers
        except Exception as e:
            print(e)
            status, headers_list = "500 Internal Server Error", [("Content-Type", "text/plain")]
            body_iterator = [b"Internal Server Error"]

        return self._generate_http_response(status, headers_list, body_iterator)

    def _parse_http_request(self, request: SocketIO) -> HTTPRequest:
        """Упрощенный парсинг http-запроса."""
        # Парсим request line
        request_line = request.readline()
        try:
            method, path, protocol = request_line.decode("ascii").strip().split()
        except ValueError:
            raise ValueError("Invalid request line")

        # Парсим headers
        headers: dict[str, str] = {}
        while True:
            line = request.readline()
            if not line or line in (b"\r\n", b"\n"):
                break

            try:
                name, value = line.decode("ascii").split(":", 1)
            except ValueError:
                raise ValueError(f"Invalid header line: {line!r}")

            headers[name.strip()] = value.strip()

        return HTTPRequest(
            method=method,
            path=path,
            protocol=protocol,
            headers=headers,
            # Оставшуюся часть запроса передаем как body
            body=request,
        )

    def _generate_environ(self, http_request: HTTPRequest) -> dict:
        """Формируем environ для wsgi-приложения."""
        path, _, query_string = http_request.path.partition("?")
        environ = {
            "REQUEST_METHOD": http_request.method,
            "SCRIPT_NAME": "",
            "PATH_INFO": path,
            "QUERY_STRING": query_string,
            "CONTENT_TYPE": http_request.headers.get("Content-Type", ""),
            "CONTENT_LENGTH": http_request.headers.get("Content-Length", ""),
            "SERVER_NAME": self.host,
            "SERVER_PORT": str(self.port),
            "SERVER_PROTOCOL": http_request.protocol,
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
            "wsgi.input": http_request.body,
            "wsgi.errors": None,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
        }
        # Добавляем http-заголовки
        for key, value in http_request.headers.items():
            environ[f"HTTP_{key.upper().replace('-', '_')}"] = value
        return environ

    def _generate_http_response(
        self,
        status: str,
        headers_list: list[tuple[str, str]],
        body_iterator: Iterator[bytes],
    ) -> Iterator[bytes]:
        """Формируем HTTP-ответ."""
        # Сначала собираем тело в память, чтобы посчитать Content-Length
        body_chunks = list(body_iterator)

        # Формируем заголовки
        response_lines = [f"HTTP/1.1 {status}"]
        for k, v in headers_list:
            response_lines.append(f"{k}: {v}")
        # "\r\n\r\n" перед телом
        response_lines.append("")
        response_lines.append("")

        # yield заголовков
        yield ("\r\n".join(response_lines).encode("iso-8859-1"))
        # yield тела
        yield from body_chunks
