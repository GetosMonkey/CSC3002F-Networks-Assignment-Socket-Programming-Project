import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from socket import *
import threading
from protocol import receive_packet, encode_packet  # type: ignore
from client_handler import handle_client

SERVER_PORT = 12001
SERVER_HOST = ''

def start_server():
    server_socket = socket(AF_INET, SOCK_STREAM)
    # This line tells the OS to allow us to reuse the port immediately if it's lingering
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)

    print(f"TCP Server is ready to receive connections on port {SERVER_PORT}...")

    while True:
        connection_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")

        threading.Thread(
            target=handle_client,
            args=(connection_socket, addr)
        ).start()


    print(f"Connection closed: {addr}")
    connection_socket.close()

if __name__ == "__main__":
    start_server()