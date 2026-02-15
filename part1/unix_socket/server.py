import os
import socket

ADDR = "/tmp/demo.sock"

# Если файл остался от прошлого запуска
if os.path.exists(ADDR):
    os.remove(ADDR)

# Создаем сокет
server_socket = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)

server_socket.bind(ADDR)
server_socket.listen()

print("Python: сервер слушает: ", ADDR)

client_socket, client_address = server_socket.accept()

print(f"Python: клиент подключился, его адрес: {client_address}")


data = client_socket.recv(1024)
print("Python: клиент отправил:", data.decode())
client_socket.send(b"Your data processed")

client_socket.close()
server_socket.close()
