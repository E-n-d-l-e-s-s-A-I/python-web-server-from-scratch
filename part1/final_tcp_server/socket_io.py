import io
import logging
import select
import socket
import time
from threading import Event


class SocketIO(io.RawIOBase):
    def __init__(
        self,
        socket: socket.socket,
        shutdown_event: Event,
        poll_interval: float = 0.5,
        idle_timeout: float = 5,
        shutdown_timeout: float = 10,
    ):
        self.socket = socket
        self.poll_interval = poll_interval
        self.idle_timeout = idle_timeout
        self.shutdown_timeout = shutdown_timeout

        # Внутренний буфер: recv() может вернуть больше данных, чем запросил read(size).
        # Остаток сохраняется здесь до следующего вызова read().
        self.buffer = bytearray()

        self.deadline = time.perf_counter() + self.idle_timeout
        self.shutdown_event = shutdown_event
        self.shutdown_deadline_set = False

        self.is_socket_end = False

    def _recv(self, chunk_size: int) -> bytes:
        """
        Низкоуровневое чтение из сокета с поддержкой таймаутов.
        Возвращает до chunk_size байт или b"" если соединение закрыто.
        """
        if self.is_socket_end:
            return b""

        while True:
            # При получении сигнала завершения переключаемся на shutdown_timeout
            if self.shutdown_event.is_set() and not self.shutdown_deadline_set:
                self.deadline = time.perf_counter() + self.shutdown_timeout
                self.shutdown_deadline_set = True

            # Ждём готовности сокета не дольше poll_interval,
            # чтобы периодически проверять таймауты и флаг завершения
            ready, _, _ = select.select([self.socket], [], [], self.poll_interval)
            if ready:
                # Клиент прислал данные - сбрасываем idle-таймаут
                if not self.shutdown_deadline_set:
                    self.deadline = time.perf_counter() + self.idle_timeout

                chunk = self.socket.recv(chunk_size)
                if chunk:
                    return chunk

                else:
                    logging.debug("Python: клиент прислал (FIN).")
                    self.is_socket_end = True
                    return b""

            if time.perf_counter() > self.deadline:
                logging.warning("Python: timeout ожидания клиента")
                raise TimeoutError("Клиент слишком долго отправлял данные")

    def read(self, size=-1) -> bytes:
        """
        Возвращает ровно size байт из сокета (или меньше, если соединение закрыто).
        При size < 0 читает всё до конца соединения.
        """

        if size < 0:
            # Режим "читаем всё": забираем буфер и дочитываем сокет до конца
            chunks = [bytes(self.buffer)]
            self.buffer = bytearray()
            while chunk := self._recv(1024):
                chunks.append(chunk)
            return b"".join(chunks)
        else:
            # Режим "читаем ровно size байт": дочитываем в буфер, пока не наберём нужное количество
            while len(self.buffer) < size:
                chunk = self._recv(size - len(self.buffer))
                if not chunk:
                    break
                self.buffer.extend(chunk)

            to_return = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return bytes(to_return)

    def readinto(self, b: bytearray) -> int:
        """Записывает данные из сокета в байтовый буфер b."""
        data = self.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def readline(self, size=-1) -> bytes:
        """
        Читает одну строку (до символа \\n включительно).
        Побайтовое чтение через read(1) — не самый эффективный способ,
        но корректный: мы не рискуем "проскочить" конец строки и захватить
        данные следующего запроса. Production-серверы используют BufferedReader
        для снижения накладных расходов.
        """
        line = bytearray()
        while size < 0 or len(line) < size:
            c = self.read(1)
            if not c:
                break
            line.extend(c)
            if c == b"\n":
                break
        return bytes(line)

    def readlines(self, hint=-1) -> list[bytes]:
        """Возвращает строки, лимит количества прочитанных байт задаётся через hint."""
        lines = []
        total = 0
        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
            total += len(line)
            if 0 < hint <= total:
                break
        return lines

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line
