import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from socket import *
import threading
from protocol import receive_packet, encode_packet
from client_handler import handle_client
from database.db_connection import initialize_database

SERVER_PORT = 12001
SERVER_HOST = ''

UDP_PORT = 13000
udp_server = socket(AF_INET, SOCK_DGRAM)
udp_server.bind(("localhost", UDP_PORT))
udp_clients = []

UDP_PORT = 13000
udp_server = socket(AF_INET, SOCK_DGRAM)
udp_server.bind(("localhost", UDP_PORT))
udp_clients = []

#active_clients = [] # Shared list for broadcasting
authenticated_clients = []

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
        threading.Thread(target=udp_server_handler, daemon=True).start()
        threading.Thread(
            target=handle_client,
            args=(connection_socket, addr, authenticated_clients) # Pass the list
        ).start()
        


def udp_server_handler():
    while True:
        message, addr = udp_server.recvfrom(1024)

        if addr not in udp_clients:
            udp_clients.append(addr)

        for client in udp_clients:
            if client != addr:
                udp_server.sendto(message, client)


if __name__ == "__main__":
    initialize_database()
    start_server()
   
