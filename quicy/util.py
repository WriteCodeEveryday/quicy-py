from struct import unpack


def get_variable_length_integer_octet_size(first_octect):
    """Get the number of octets representing the variable-length integer.

    See also "7.1. Variable-Length Integer Encoding".
    """
    (first_octet,) = unpack('>B', first_octect)
    first_two_bits = first_octet >> 6

    if first_two_bits == 0b11:    # 0b11xxxxxx set
        return 8
    elif first_two_bits == 0b10:  # 0b10xxxxxx set
        return 4
    elif first_two_bits == 0b01:  # 0b01xxxxxx set
        return 2
    else:                         # 0b00xxxxxx set
        return 1


def parse_variable_length_integer(binary_data):
    """Get the value of a variable length integer.

    See also "7.1. Variable-Length Integer Encoding".
    """
    octets = len(binary_data)

    if octets == 8:
        (length,) = unpack('>Q', binary_data)
        return length & 0x3FFFFFFFFFFFFFFF  # clear top 2 bits
    elif octets == 4:
        (length,) = unpack('>I', binary_data)
        return length & 0x3FFFFFFF  # clear top 2 bits
    elif octets == 2:
        (length,) = unpack('>H', binary_data)
        return length & 0x3FFF  # clear top 2 bits
    elif octets == 1:
        (length,) = unpack('>B', binary_data)
        return length & 0x3F  # clear top 2 bits
    else:
        raise ValueError('Variable-length integer must be encoded in 1, 2, 4 or 8 octets. (Got {})'.format(octets))
