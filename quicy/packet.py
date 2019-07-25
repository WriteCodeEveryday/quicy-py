from abc import ABC, abstractmethod
from struct import pack, unpack

from constants import VERSION_NEGOTIATION
from util import get_variable_length_integer_octet_size, parse_variable_length_integer


class QuicPacket(ABC):
    @staticmethod
    def get_packet_number_octet_length(first_packet_number_octect):
        """Get the number of octets representing the packet number.

        See also "4.8. Packet Numbers".
        """
        (first_octet,) = unpack('>B', first_packet_number_octect)
        first_two_bits = first_octet >> 6

        if first_two_bits == 0b11:    # 0b11xxxxxx set
            return 4
        elif first_two_bits == 0b10:  # 0b10xxxxxx set
            return 2
        else:                         # 0b0xxxxxxx set
            return 1

    @staticmethod
    def parse_packet_number(binary_data):
        """Get the packet number for the packet.

        See also "4.8. Packet Numbers".
        """
        octets = len(binary_data)

        if octets == 4:
            (pnum,) = unpack('>I', binary_data)
            return pnum & 0x3FFFFFFF  # clear top 2 bits
        elif octets == 2:
            (pnum,) = unpack('>H', binary_data)
            return pnum & 0x7FFF  # clear top bit
        elif octets == 1:
            (pnum,) = unpack('>B', binary_data)
            return pnum
        else:
            raise ValueError('Packet number must be encoded in 1, 2 or 4 octets. (Got {})'.format(octets))

    @abstractmethod
    def deserialize(self, binary_data):
        pass

    @abstractmethod
    def serialize(self):
        pass


class LongHeader(QuicPacket):
    def __init__(self, binary_data):
        self.deserialize(binary_data)

    def get_packet_type(self):
        return self._packet_type

    def deserialize(self, binary_data):
        """Deserialize data in Long Header Format.

        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+
        |1|   Type (7)  |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                         Version (32)                          |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |DCIL(4)|SCIL(4)|
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |               Destination Connection ID (0/32..144)         ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                 Source Connection ID (0/32..144)            ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                           Length (i)                        ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                     Packet Number (8/16/32)                   |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                          Payload (*)                        ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        See also "4.1. Long Header".
        """
        data_start_index = 0

        # parse type
        data_len = 1
        (type_octet,) = unpack('>B', binary_data[data_start_index:data_start_index + data_len])
        self._packet_type = type_octet & 0x7F
        data_start_index += data_len

        # parse version
        data_len = 4
        (version,) = unpack('>I', binary_data[data_start_index:data_start_index + data_len])
        self._version = version
        data_start_index += data_len

        # parse destination connection ID length (DCIL) and source connection ID length (SCIL)
        data_len = 1
        (lengths,) = unpack('>B', binary_data[data_start_index:data_start_index + data_len])
        self._dcil = lengths >> 4
        self._scil = lengths & 0xF
        data_start_index += data_len

        # parse the destination connection ID
        data_len = self._dcil
        (dci,) = unpack('>s', binary_data[data_start_index:data_start_index + data_len])
        self._dest_conn_id = dci
        data_start_index += data_len

        # parse the source connection ID
        data_len = self._scil
        (sci,) = unpack('>s', binary_data[data_start_index:data_start_index + data_len])
        self._src_conn_id = sci
        data_start_index += data_len

        # parse the length
        data_len = get_variable_length_integer_octet_size(binary_data[data_start_index])
        self._length = parse_variable_length_integer(binary_data[data_start_index:data_start_index + data_len])
        data_start_index += data_len

        # parse the packet number
        data_len = QuicPacket.get_packet_number_octet_length(binary_data[data_start_index])
        self._packet_number = QuicPacket.parse_packet_number(binary_data[data_start_index:data_start_index + data_len])
        data_start_index += data_len

        # parse the payload
        data_len = self._length - data_len  # length - packet number length
        (payload,) = unpack('>s', binary_data[data_start_index:data_start_index + data_len])
        self._payload = payload

        return data_start_index + data_len

    def serialize(self):
        pass


class ShortHeader(QuicPacket):
    def __init__(self, binary_data):
        self.deserialize(binary_data)

    def deserialize(self, binary_data):
        pass

    def serialize(self):
        pass


class VersionNegotiationPacket(QuicPacket):
    def __init__(self, binary_data):
        self.deserialize(binary_data)

    def deserialize(self, binary_data):
        """Deserialize a Version Negotiation Packet.

        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+
        |1|  Unused (7) |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                          Version (32)                         |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |DCIL(4)|SCIL(4)|
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |               Destination Connection ID (0/32..144)         ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                 Source Connection ID (0/32..144)            ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                    Supported Version 1 (32)                 ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                   [Supported Version 2 (32)]                ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                                       ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                   [Supported Version N (32)]                ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        See also "4.3. Version Negotiation Packet".
        """
        data_start_index = 1  # first octet unused

        # parse version
        data_len = 4
        (version,) = unpack('>I', binary_data[data_start_index:data_start_index + data_len])
        if version != VERSION_NEGOTIATION:
            raise ValueError('A Version Negotiation packet must have version 0x00000000 ' +
                             '(received version 0x{:08X})'.format(version))
        self._version = version
        data_start_index += data_len

        # parse destination connection ID length (DCIL) and source connection ID length (SCIL)
        data_len = 1
        (lengths,) = unpack('>B', binary_data[data_start_index:data_start_index + data_len])
        self._dcil = lengths >> 4
        self._scil = lengths & 0xF
        data_start_index += data_len

        # parse the destination connection ID
        data_len = self._dcil
        (dci,) = unpack('>s', binary_data[data_start_index:data_start_index + data_len])
        self._dest_conn_id = dci
        data_start_index += data_len

        # parse the source connection ID
        data_len = self._scil
        (sci,) = unpack('>s', binary_data[data_start_index:data_start_index + data_len])
        self._src_conn_id = sci
        data_start_index += data_len

        # parse supported versions
        data_len = 4
        self._supported_versions = set()
        for version_index in range(data_start_index, data_len, len(binary_data)):
            (version,) = unpack('>I', binary_data[data_start_index:data_start_index + data_len])
            self._supported_versions.add(version)

    def serialize(self):
        pass


class CryptoHandshakeInitialPacket(LongHeader):
    def __init__(self, binary_data):
        self.deserialize(binary_data)

    def deserialize(self, binary_data):
        """Deserialize a Cryptographic Handshake Initial Packet.

        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                      Token Length (i)  ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                            Token (*)                        ...
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        See also "4.4.1. Initial Packet".
        """
        # parse the long header
        data_start_index = super().deserialize(binary_data)

        # parse the length
        data_len = get_variable_length_integer_octet_size(binary_data[data_start_index])
        self._token_length = parse_variable_length_integer(binary_data[data_start_index:data_start_index + data_len])
        data_start_index += data_len

        # parse the token
        data_len = self._token_length
        (token,) = unpack('>s', binary_data[data_start_index:data_start_index + data_len])
        self._token = token

    def serialize(self):
        pass
