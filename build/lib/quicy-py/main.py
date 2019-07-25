from argparse import ArgumentParser

from client import QuicClient
from constants import LOCALHOST
from server import QuicServer


def main():
    parser = ArgumentParser(description='Run the QUIC protocol')
    parser.add_argument('--ip', metavar='IP', type=str, nargs='?', default=LOCALHOST,
                        help='The IP address to connect to')
    parser.add_argument('--port', metavar='PORT', type=int, nargs='?', default=1620, help='The port to connect to')
    args = parser.parse_args()

    if args.ip == LOCALHOST:
        server = QuicServer(args.ip, args.port)

    client = QuicClient(args.ip, args.port)


if __name__ == '__main__':
    main()
