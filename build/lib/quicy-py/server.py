from socket import socket, AF_INET, SOCK_DGRAM


class QuicServer:
    def __init__(self, ip, port):
        self._connection = socket(AF_INET, SOCK_DGRAM)
        self._connection.bind((ip, port))
        print('[*] Server listening at {}:{}'.format(ip, port))
