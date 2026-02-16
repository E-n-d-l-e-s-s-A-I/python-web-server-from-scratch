import signal
import socket


def signal_handler(signum, frame):
    print(f"Python: получен сигнал; {signum}")
    print(f"Python: frame: {frame}")


signal.signal(signal.SIGTERM, signal_handler)

ADDR = ("127.0.0.1", 9999)
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server_socket.bind(ADDR)
server_socket.listen()

client_socket, _ = server_socket.accept()

server_socket.close()
client_socket.close()
