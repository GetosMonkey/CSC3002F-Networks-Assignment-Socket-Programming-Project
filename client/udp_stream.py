from socket import *

SERVER_HOST = "localhost"
SERVER_PORT = 12001


def send_udp_message():
    client_socket = socket(AF_INET, SOCK_DGRAM)

    message = input("Enter UDP message: ")
    client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))

    response, _ = client_socket.recvfrom(2048)
    print("From UDP Server:", response.decode())

    client_socket.close()


if __name__ == "__main__":
    send_udp_message()