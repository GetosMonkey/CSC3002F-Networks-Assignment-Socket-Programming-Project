def encode_packet(sequence_number, message_type, body_text):
    """
    Encodes a message into a simple text format followed by a newline.
    (Kept simple to be compatible with a raw socket client like telnet or `tcp_client.py`)
    """
    if not body_text.endswith('\n'):
        body_text += '\n'
    return body_text.encode('utf-8')

def receive_packet(sock):
    """
    Reads a simple string message from the socket.
    """
    try:
        data = sock.recv(1024)
        if not data:
            return None, None, None # Connection closed
            
        body_text = data.decode('utf-8').strip()
        return 1, "DATA", body_text
    except Exception:
        return None, None, None
    
