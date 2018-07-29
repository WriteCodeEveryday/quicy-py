from struct import pack
import unittest

from util import get_variable_length_integer_octet_size, parse_variable_length_integer


class TestVariableLengthIntegers(unittest.TestCase):
    def test_get_variable_length_integer_octet_size(self):
        for i in range(0x100):
            octet = pack('>B', i)
            length = get_variable_length_integer_octet_size(octet)

            if i < 0b01000000:
                self.assertEqual(length, 1)
            elif i < 0b10000000:
                self.assertEqual(length, 2)
            elif i < 0b11000000:
                self.assertEqual(length, 4)
            else:
                self.assertEqual(length, 8)

    def test_parse_variable_length_integer(self):
        tests = [
            (b'\xC2\x19\x7C\x5E\xFF\x14\xE8\x8C', 151288809941952652),
            (b'\x9D\x7F\x3E\x7D', 494878333),
            (b'\x7B\xBD', 15293),
            (b'\x40\x25', 37),
            (b'\x25', 37)
        ]

        for (input, expected) in tests:
            parsed = parse_variable_length_integer(input)
            self.assertEqual(parsed, expected)

        with self.assertRaises(ValueError):
            parse_variable_length_integer('\x00\x00\x00')  # invalid length


if __name__ == '__main__':
    unittest.main()
