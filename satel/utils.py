import logging

_LOGGER = logging.getLogger(__name__)


def checksum(command):
    crc = 0x147A
    for b in command:
        crc = ((crc << 1) & 0xFFFF) | (crc & 0x8000) >> 15
        crc = crc ^ 0xFFFF
        crc = (crc + (crc >> 8) + b) & 0xFFFF
    return crc


def toHex(data):
    hex_msg = ""
    for c in data:
        hex_msg += "\\x" + format(c, "02x")
    return hex_msg


def verify_and_strip(resp):
    if resp[0:2] != b"\xFE\xFE":
        _LOGGER.error("Invalid header: %s" % toHex(resp))
        raise ValueError(f"Invalid header: {resp[0]:X}{resp[1]:X}")
    if resp[-2:] != b"\xFE\x0D":
        _LOGGER.error("Invalid footer: %s" % toHex(resp))
        raise ValueError(f"Invalid footer: {resp[-2]:X}{resp[-1]:X}")

    output = resp[2:-2].replace(b"\xFE\xF0", b"\xFE")

    c = checksum(bytearray(output[0:-2]))
    if (256 * output[-2:-1][0] + output[-1:][0]) != c:
        raise ValueError(
            "Invalid checksum. Got %d expected %d"
            % ((256 * output[-2:-1][0] + output[-1:][0]), c)
        )

    return output[0:-2]


def list_set_bits(r, expected_length):
    """Return list of positions of bits set to one in given data.
    This method is used to read e.g. violated zones. They are marked by ones
    on respective bit positions - as per Satel manual.
    """
    set_bit_numbers = []
    bit_index = 0x1
    assert len(r) == expected_length

    for b in r:
        for i in range(8):
            if ((b >> i) & 1) == 1:
                set_bit_numbers.append(bit_index)
            bit_index += 1

    return set_bit_numbers


def generate_query(command):
    data = bytearray(command)
    c = checksum(data)
    data.append(c >> 8)
    data.append(c & 0xFF)
    data = data.replace(b"\xFE", b"\xFE\xF0")
    data = bytearray.fromhex("FEFE") + data + bytearray.fromhex("FE0D")
    return data


def output_bytes(output):
    _LOGGER.debug("output_bytes")
    output_no = 1 << output - 1
    return output_no.to_bytes(32, "little")


def partition_bytes(partition_list):
    ret_val = 0
    for position in partition_list:
        if position >= 32:
            raise IndexError("Partition index to high: %d" % position)
        ret_val = ret_val | (1 << (position - 1))

    return ret_val.to_bytes(4, "little")


def getCodeBytes(code):
    while len(code) < 16:
        code += "F"
    code_bytes = bytearray.fromhex(code)
    return code_bytes
