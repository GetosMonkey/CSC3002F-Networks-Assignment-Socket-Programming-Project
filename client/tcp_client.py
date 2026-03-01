from socket import *

SERVER_HOST = "localhost"
SERVER_PORT = 12000


def start_client():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    print("Connected to server.")

    while True:
        message = input("Enter message (or 'exit'): ")

        if message.lower() == "exit":
            break

        client_socket.send(message.encode())

        response = client_socket.recv(1024)
        print("From Server:", response.decode())

    client_socket.close()


if __name__ == "__main__":
    start_client()