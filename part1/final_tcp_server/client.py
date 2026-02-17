import socket
import sys

SOCK_ADDRESS = ("127.0.0.1", 9999)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect(SOCK_ADDRESS)
except Exception:
    sys.exit("Сервер недоступен")


with client_socket:
    while True:
        user_input = input("Python: клиентский ввод - ")
        if user_input == "exit":
            break

        client_socket.send(user_input.encode() + b"\n")

        server_response = client_socket.recv(1024)
        if not server_response:
            print("Python: получен (FIN) от сервера")
            break

        print(f"Python: ответ сервера - {server_response.decode()}")
