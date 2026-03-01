from socket import *

SERVER_PORT = 12001

def start_udp_server():
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('', SERVER_PORT))

    print("UDP Server ready...")

    while True:
        message, client_address = server_socket.recvfrom(2048)
        print("Received:", message.decode())

        response = message.decode().upper()
        server_socket.sendto(response.encode(), client_address)


if __name__ == "__main__":
    start_udp_server()