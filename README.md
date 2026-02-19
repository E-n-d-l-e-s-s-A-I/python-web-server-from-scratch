# Внутреннее устройство веб-сервера

Код к серии статей, в которой мы разбираем, как устроены веб-серверы на Python - от системных вызовов Linux до WSGI и ASGI.

## Часть 1: от syscalls до WSGI

[Ссылка на статью]()

В первой части мы проходим путь от сокетов и системных вызовов до работающего WSGI-сервера.

### Структура

```
part1/
├── unix_socket/                        # Взаимодействие через AF_UNIX сокеты
├── tcp_socket/                         # Взаимодействие через TCP сокеты
├── socket_as_fd/                       # HTTP-запрос через read()/write()
├── process_sleeping/                   # Демонстрация состояния процесса при ожидании соединений
├── simple_tcp_server/                  # TCP-сервер с эхо-обработчиком
├── tcp_server_with_idle_timeout/       # + idle-timeout через select()
├── tcp_server_with_graceful_shutdown/  # + graceful shutdown через обработку сигналов
├── final_tcp_server/                   # + SocketIO (файловый интерфейс над сокетом)
└── wsgi/                               # WSGI-обработчик + Flask-приложение
```

### Запуск

```bash
# Зависимости
uv sync

# WSGI-сервер с Flask
uv run -m wsgi.app
```