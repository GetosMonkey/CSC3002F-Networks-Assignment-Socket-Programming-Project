from socket import *
import threading
import os

SERVER_HOST = "localhost"
SERVER_PORT = 12001

def authenticate(username, password, client_socket):
    message_string = "Authenticate/" + username + "/" + password
    client_socket.send(message_string.encode())

# Checks to see if the user is authenticated
def login(client_socket):
    username = input("Enter username: ")
    password = input("Enter password:  ")
    authenticate(username, password, client_socket)
    response = client_socket.recv(1024).decode().strip()
    if response == "SUCCESS":
        return True
    else:
        print(f"Login failed! (Server said: {response})")
        return False

# Captures the new user's details and sends it to the server for a SUCCESS-ful account creation
def sign_up(client_socket):
    username = input("Enter a new username: ")
    password = input("Enter a new password: ")
    message_string = "NewUser" + "/" + username + "/" + password
    client_socket.send(message_string.encode())
    response = client_socket.recv(1024).decode().strip()
    if response == "SUCCESS":
        print("Sign-up successful!")
        return True
    else:
        print(f"Sign-up failed: {response}")
        return False

#Prompts the user to login or sign-up, with options of logging in for existing users or a sign-up for new users
def show_menu():
    print("\n-- Welcome to WhatsUp --")
    print("1. Login")
    print("2. Sign-up")
    print("q. Quit")
    reply = input("Select an option by number or q to quit: ")
    return reply

# Gives user the outline for the expected format of a valid input string depending on what type of operation they want to execute
def show_commands():
    print("\n-- Command Pallete --")
    print("Follow the syntax for each command to execute automatically:")
    print("1. Private Message (Syntax: /pm <user> <message>)")
    print("2. Message Group (Syntax: /group <group_id> <message>)")
    print("3. Send File (Syntax: /file <user> <filename> OR /file <group_name> <filename> )")
    print("4. Create New Group (Syntax: /create <group_name>)")
    print("5. Join Group (Syntax: /join <group_id>)")
    print("Type 'logout' to return to menu.")
    print("Type 'quit' to exit.")

# Continuously listens for messages from the server and prints them to the terminal
def receive_messages(client_socket, stop_event):
    while not stop_event.is_set():
        try:
            client_socket.settimeout(1.0) 
            try:
                message = client_socket.recv(1024).decode().strip()
                if not message:
                    break
                print(f"\n{message}")
            except timeout:
                continue
        except:
            print("\nDisconnected from server.")
            break

# Starts the client and handles the orchestration of our frontend, equivalent to a main class
def start_client():
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")
    except Exception as e:
        print(f"Could not connect to server: {e}")
        return

    stop_listener = threading.Event()

    while True: 
        authenticated = False
        
        while not authenticated: # Looping on the login menu until a user is successully authenticated
            choice = show_menu()
            if choice == "1":
                authenticated = login(client_socket)
            elif choice == "2":
                authenticated = sign_up(client_socket)
            elif choice.lower() == "q":
                client_socket.close()
                return
            else:
                print("Invalid Input!")

        stop_listener.clear()
        listener_thread = threading.Thread(target=receive_messages, args=(client_socket, stop_listener))
        listener_thread.daemon = True # Ensure thread closes when main program exits
        listener_thread.start()

        print("\nAuthenticated successfully!")
        show_commands()

        while True:
            message = input("> ")
            if message.lower() == "quit":
                client_socket.close()
                return
            
            if message.lower() == "logout":
                print("Logging out...")
                stop_listener.set() # Stop the background thread
                listener_thread.join() # Wait for it to exit
                client_socket.settimeout(None)
                break # Return to login menu

            if message.startswith("/file"):
                fileshare(message)

def fileshare(message):
    parts= message.split(" ")
    id = parts[1]
    filename = parts[2]

    






if __name__ == "__main__":
    start_client()
