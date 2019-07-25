from socket import socket, AF_INET, SOCK_DGRAM


class QuicClient:
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._connection = socket(AF_INET, SOCK_DGRAM)

    def send_message(self, message):
        self._connection.sendto(message, (self._ip, self._port))
