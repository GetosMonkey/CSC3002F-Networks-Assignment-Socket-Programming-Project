import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from socket import *
import threading
from protocol import receive_packet, encode_packet  # type: ignore

SERVER_PORT = 12005
SERVER_HOST = ''

def start_server():
    server_socket = socket(AF_INET, SOCK_STREAM)
    # This line tells the OS to allow us to reuse the port immediately if it's lingering
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)

    print("TCP Server is ready to receive connections...")

    while True:
        connection_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")

        threading.Thread(
            target=handle_client,
            args=(connection_socket, addr)
        ).start()


def handle_client(connection_socket, addr):
    while True:
        try:
            sequence_number, message_type, body = receive_packet(connection_socket)
            if sequence_number is None: # Connection closed
                break

            print(f"[{addr}] Received: {body}")

            response_body = f"Server received: {body}"
            response_packet = encode_packet(sequence_number, "ACK", response_body)
            connection_socket.sendall(response_packet)

        except Exception as e:
            print(f"Error with {addr}: {e}")
            break

    print(f"Connection closed: {addr}")
    connection_socket.close()

if __name__ == "__main__":
    start_server()