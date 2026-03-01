from socket import *
import threading

SERVER_PORT = 12000
SERVER_HOST = ''


def start_server():
    server_socket = socket(AF_INET, SOCK_STREAM)
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
            data = connection_socket.recv(1024)
            if not data:
                break

            message = data.decode()
            print(f"[{addr}] {message}")

            # Echo back for now
            connection_socket.send(f"Server received: {message}".encode())

        except:
            break

    print(f"Connection closed: {addr}")
    connection_socket.close()


if __name__ == "__main__":
    start_server()