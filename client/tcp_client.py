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

def login():
    username = input("Enter username: ")

def show_menu():
    print("Welcome to ChatApp!") ## This method prompts the user to Login or sign-up
    print("1. Login") ## Login for existing users
    print("2. Sign-up") ## sign-up for new users
    reply = input("Select option: ")
    return reply

 
def sign_up():
    username=input()


def main():
    ##start_client()
    choice = show_menu()

    if choice =="1":
        login()
    elif choice =="2":
        sign_up()
    else:
        print("Invalid Input!")





if __name__ == "__main__":
    main()