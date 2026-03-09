import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from socket import *
import threading
from protocol import receive_packet, encode_packet
from client_handler import handle_client

SERVER_PORT = 12001
SERVER_HOST = ''

#active_clients = [] # Shared list for broadcasting
authenticated_clients = {}

# Creates/starts a multithreaded TCP server connected to por 12001 that loops infinitely to accept new ConnectionResetError
# For every new client a new thread is made/opened
def start_server():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)

    print(f"TCP Server is ready to receive connections on port {SERVER_PORT}...")

    while True:
        connection_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")

        threading.Thread(
            target=handle_client,
            args=(connection_socket, addr, authenticated_clients) # Pass the list
        ).start()


    print(f"Connection closed: {addr}")
    connection_socket.close()

if __name__ == "__main__":
    start_server()