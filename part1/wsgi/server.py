from final_tcp_server.server import TCPServer

from .handler import WSGIHandler

class WSGIServer(TCPServer):
    def __init__(
        self,
        host,
        port,
        app,
        poll_interval=0.5,
        client_idle_timeout=5,
        shutdown_timeout=10,
    ):
        handler = WSGIHandler(app, host, port)
        super().__init__(host, port, handler, poll_interval, client_idle_timeout, shutdown_timeout)
