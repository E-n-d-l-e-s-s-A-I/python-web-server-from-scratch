import socket

ADDR = "/tmp/demo.sock"

client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client_socket.connect(ADDR)

data = "Hello from UNIX socket client"
client_socket.send(data.encode())
reply = client_socket.recv(1024)
print("Python: ответ сервера:", reply.decode())

client_socket.close()
