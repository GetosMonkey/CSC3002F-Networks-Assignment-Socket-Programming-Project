import struct

# Header format:
# 4 bytes sequence number
# 4 bytes content length

HEADER_FORMAT = "!II"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def encode_packet(sequence_number, body_bytes):
    content_length = len(body_bytes)
    header = struct.pack(HEADER_FORMAT, sequence_number, content_length)
    return header + body_bytes

def decode_header(header_bytes):
    return struct.unpack(HEADER_FORMAT, header_bytes)

def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def receive_packet(sock):
    header = recv_exact(sock, HEADER_SIZE)
    if not header:
        return None, None

    sequence_number, content_length = decode_header(header)

    body = recv_exact(sock, content_length)
    if not body:
        return None, None

    return sequence_number, body