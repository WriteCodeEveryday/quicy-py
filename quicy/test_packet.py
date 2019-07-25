from struct import pack
import unittest

from packet import QuicPacket


class TestQuicPacket(unittest.TestCase):
    def test_get_packet_number_octet_length(self):
        for i in range(0x100):
            octet = pack('>B', i)
            length = QuicPacket.get_packet_number_octet_length(octet)

            if i < 0b10000000:
                self.assertEqual(length, 1)
            elif i < 0b11000000:
                self.assertEqual(length, 2)
            else:
                self.assertEqual(length, 4)

    def test_parse_packet_number(self):
        tests = [
            (b'\xFF\xFF\xFF\xFF', 0x3FFFFFFF),
            (b'\xC1\x23\x45\x67', 0x1234567),
            (b'\xBF\xFF', 0x3FFF),
            (b'\x7F', 0x7F)
        ]

        for (input, expected) in tests:
            parsed = QuicPacket.parse_packet_number(input)
            self.assertEqual(parsed, expected)

        with self.assertRaises(ValueError):
            QuicPacket.parse_packet_number('\x00\x00\x00')  # invalid length


if __name__ == '__main__':
    unittest.main()
