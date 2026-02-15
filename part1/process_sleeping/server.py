import socket

ADDR = ("127.0.0.1", 9999)


# Создаем сокет
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

# Нужно для повторного использования адреса при перезапуске программы
# Иначе он будет на некоторое время зарезервирован ядром
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(ADDR)
server_socket.listen()

print("Python: сервер слушает: ", ADDR)

client_socket, client_address = server_socket.accept()

print(f"Python: клиент подключился, его адрес: {client_address}")


data = client_socket.recv(1024)
print("Python: клиент отправил:", data.decode())
client_socket.send(b"Your data received from TCP socket")
client_socket.close()

counter = 0
try:
    while True:
        counter += 1
finally:
    server_socket.close()
