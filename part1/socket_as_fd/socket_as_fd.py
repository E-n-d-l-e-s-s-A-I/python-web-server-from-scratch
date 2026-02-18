import os
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# DNS в этой статье не рассматривается, поэтому используем ip-адрес
# Актуальный адрес домена host example.com можно посмотреть командой
# host example.com
# Скорее всего это будет ip cloudflare
# Поэтому обязательно указываем доменное имя в заголовке запроса
client_socket.connect(("8.6.112.0", 80))

# Получаем номер файлового дескриптора
fd = client_socket.fileno()

data = b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n"

# Пишем в сокет, через общий для файловых дескрипторов системный вызов write
os.write(fd, data)

# Читаем из сокета через системный вызов read
response = os.read(fd, 4096)
print(response.decode())

client_socket.close()
