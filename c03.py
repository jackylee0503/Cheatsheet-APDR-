"""
Sensor Telemetry Decoder

A weather-station network with mixed-endianness boards; raw byte packets must be parsed manually (the struct module is banned).
"""
#took 2 days to do with my hand 

# Task 01
def bytes_to_uint(data, endianness="big"):
    if endianness not in ("big", "little"):
        raise ValueError("endianness must be 'big' or 'little'")
    if endianness == "little":
        data = data[::-1]
    total = 0
    for byte in data:
        total = (total << 8) | byte
    return total


def uint_to_bytes(value, width, endianness="big"):
    return value.to_bytes(width, byteorder=endianness)


# Task 02
def bytes_to_int_twos_complement(data, endianness="big"):
    if endianness not in ("big", "little"):
        raise ValueError("endianness must be 'big' or 'little'")
    if not data:
        raise ValueError("data must not be empty")
    if endianness == "little":
        data = data[::-1]
    total = 0
    for byte in data:
        total = (total << 8) | byte

    n = 8 * len(data)
    if (total >> (n - 1)) & 1:
        total -= 1 << n

    return total


# Task 03
#honestly I used claude lol sry!!!! but bsc 1st semester can do bit??? 
#but I'll make sure to understand it and write it in my own words
def bytes_to_float32(data, endianness="big"):
    u = bytes_to_uint(data, endianness)

    sign = (u >> 31) & 1
    exp  = (u >> 23) & 0xFF            # 8비트 마스크
    frac =  u        & ((1 << 23) - 1) # 23비트 마스크

    if exp == 0xFF:                    # 지수가 전부 1
        if frac == 0:
            value = float("inf")
        else:
            return float("nan")
    elif exp == 0:                     # 지수가 전부 0 → 비정규수(0 포함)
        value = (frac / 2**23) * 2**(-126)          # 앞에 1을 안 붙임
    else:                              # 일반 경우
        value = (1 + frac / 2**23) * 2**(exp - 127)

    return -value if sign else value


# Task 04
def detect_endianness(raw, known_field_range):
    uint = bytes_to_uint(raw)
    a = known_field_range[0]
    b = known_field_range[1]
    if min(a, b) <= uint <= max(a, b):
        return "big"
    else:
        return "little"


# Task 05 #realllllly hard 
#it will be good if I just use internal function iterating through dict
def parse_packet(raw, layout):
    raw_ptr = 0
    parsed_dict = {}
    for field in layout:
        name = field.get("name")
        width = field["width"]
        typ = field["type"]
        endianness = field.get("endianness", "big")
        if raw_ptr + width > len(raw):
            raise ValueError("packet truncated")
        chunk = raw[raw_ptr:raw_ptr + width]
        raw_ptr += width
        if typ == "padding":
            continue
        elif typ == "uint":
            parsed_dict[name] = bytes_to_uint(chunk, endianness)
        elif typ == "int":
            parsed_dict[name] = bytes_to_int_twos_complement(chunk, endianness)
        elif typ == "float32":
            if width != 4:
                raise ValueError("float32 field must be 4 bytes wide")
            else:
                parsed_dict[name] = bytes_to_float32(chunk, endianness)
        elif typ == "bytes":
            parsed_dict[name] = bytes(chunk)
        else:
            raise ValueError(f"unknown field type: {typ}")

    return parsed_dict


# Task 06
def validate_checksum(raw):
    if len(raw) < 1:
        return False
    payload = raw[:-1]
    claimed_checksum = raw[-1]
    checksum = sum(payload) & 0xff
    return claimed_checksum == checksum


# Task 07
def decode_stream(packets, layout):
    result = {"decoded": [], "errors": []}
    for i, packet in enumerate(packets):
        try:
            if not validate_checksum(packet):
                raise ValueError("bad checksum")
            parsed = parse_packet(packet[:-1], layout)
            result["decoded"].append(parsed)
        except (ValueError, KeyError, IndexError, TypeError) as e:
            result["errors"].append({"index": i, "reason": str(e)})
    return result


# Task 08
#yo prof why class??? it can be done with function...
class PageFaultError(Exception):
    pass


class PageTableSim:
    def __init__(self, page_size, page_table):
        self.page_size = page_size
        self.page_table = page_table

    def translate(self, virtual_addr):
        idx = virtual_addr // self.page_size
        adr = virtual_addr % self.page_size
        if idx not in self.page_table:
            raise PageFaultError(f"page {idx} is not mapped")
        else:
            return self.page_table[idx] * self.page_size + adr


# Task 09
def simulate_heap_alloc(requests, pool_size):
    x_ptr = 0
    out = []
    for request in requests:
        if x_ptr + request <= pool_size:
            out.append((x_ptr, request))
            x_ptr += request
        else:
            out.append(None)
    return out


# Task 10
def roundtrip_test(value, endianness, width):
    encode = uint_to_bytes(value, width, endianness)
    decode = bytes_to_uint(encode, endianness)
    return decode == value
