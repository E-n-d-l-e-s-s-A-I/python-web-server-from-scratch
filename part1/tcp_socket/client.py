import socket

ADDR = ("127.0.0.1", 9999)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)

data = "Hello from TCP socket client"
client_socket.send(data.encode())
reply = client_socket.recv(1024)
print("Python: ответ сервера:", reply.decode())

client_socket.close()
