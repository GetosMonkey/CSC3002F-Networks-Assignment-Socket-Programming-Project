from socket import *
import threading

SERVER_HOST = "localhost"
SERVER_PORT = 12000



def start_client():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    print("Connected to server.")

    choice = show_menu()

    authenticated = False

    if choice =="1":
        authenticated = login(client_socket)
    elif choice =="2":
        authenticated=sign_up(client_socket)
    else:
        print("Invalid Input!")

    threading.Thread(target= receive_messages, args=(client_socket,), daemon=True).start()


    show_commands()

    while authenticated:
        message = input("Select option from command list (or 'exit'): ")

        if message.lower() == "exit":
            break

        client_socket.send(message.encode())

        response = client_socket.recv(1024)
        print("From Server:", response.decode())

    client_socket.close()

def receive_messages(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        print(data)
        

def authenticate(username,password, client_socket):
    message_string="Authenticate/"+username+"/"+password
    client_socket.send(message_string.encode())



def login(client_socket):
    username = input("Enter username: ")
    password = input("Enter password:  ")
    authenticate(username,password,client_socket)
    response= client_socket.recv(1024.decode)
    if response ="SUCCESS":
        authenticated =True
    else authenticated =False


    return authenticated

def show_commands():
    print("Select a command from the list below!") ## This method prompts the user to Login or sign-up
    print("1. Private Message") ## Login for existing users
    print("2. Message Group") ## sign-up for new users
    print("3. Create New Group")
    print("4. Join Group")
    


def show_menu():
    print("Welcome to ChatApp!") ## This method prompts the user to Login or sign-up
    print("1. Login") ## Login for existing users
    print("2. Sign-up") ## sign-up for new users
    reply = input("Select option: ")
    return reply

 
def sign_up(client_socket):
    username=input("Enter a username: ")
    password=input("Enter a password: ")
    message_string=input("NewUser"+"/"+username+"/"+password)
    client_socket.send(message_string.encode())
    return valid

def main():
    ##start_client()





if __name__ == "__main__":
    main()