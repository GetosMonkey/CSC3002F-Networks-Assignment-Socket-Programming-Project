from email.mime import message
from socket import *
import threading
import os
from database.database import check_auth, register_user, append_message, get_user_by_username , get_chat_members, update_user_port, get_user_port

from udp_stream import UDPPeer

SERVER_HOST = "localhost"
SERVER_PORT = 12001
current_user = None

udp_peer = UDPPeer()

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
        global current_user
        current_user = username
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
        global current_user
        current_user = username
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
            else:
                client_socket.send(message.encode())    

def fileshare(message):
    parts= message.split(" ")
    if len(parts) < 3:
        print("Incorrect syntax used for file sharing, please specify all required arguments.")
    id = parts[1]
    filename = parts[2]

    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist!")
        return

    if get_user_by_username(id)!=None:
        send_file_to_user(id,filename)
    elif get_chat_members(id)!=None:
        send_file_to_group(id,filename)   
    else:
        print("Receiver provided is not valid.")

def send_file_to_user(id, filename):
    try:
        file_socket = socket(AF_INET, SOCK_STREAM)
        port = get_user_port(id)
        if not port:
            print(f"User {id} is not online.")
            return
        file_socket.connect(("localhost", int(port)))

        filesize = os.path.getsize(filename)

        header = f"FILE|{filename}|{filesize}"
        file_socket.send(header.encode())

        with open(filename, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                file_socket.sendall(chunk)

            file_socket.close()

        print("File sent successfully.")
    except Exception as e:
        print("Error sending file:", e)

def send_file_to_group(group_id, filename):
    members = get_chat_members(group_id)
    if not members:
        print("Group not found or has no members.")
        return

    for member in members:
        if member != current_user:  # skip yourself
            send_file_to_user(member, filename)

def p2p_client():
    file_server = socket(AF_INET, SOCK_STREAM)
    file_server.bind(("localhost", 0))  # 0 = OS picks free port
    file_server.listen()
    file_port = file_server.getsockname()[1]
    update_user_port(current_user, file_port)
    print("File server running on port:", file_port)

    while True:
        conn, addr = file_server.accept()
        threading.Thread(target=handle_incoming_file, args=(conn,), daemon=True).start()

def handle_incoming_file(conn):
    try:
        # First, receive the file header
        header = conn.recv(1024).decode()
        if not header.startswith("FILE|"):
            print("Invalid file header")
            conn.close()
            return

        # Header format: FILE|filename|filesize
        _, filename, filesize = header.split("|")
        filesize = int(filesize)

        # Prepare a new file to save
        save_path = f"received_{filename}"  
        with open(save_path, "wb") as f:
            remaining = filesize
            while remaining > 0:
                chunk = conn.recv(min(4096, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        print(f"Received file: {filename}, saved as {save_path}")

    except Exception as e:
        print("Error receiving file:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    server_thread = threading.Thread(target=p2p_client, daemon=True)
    server_thread.start()
    start_client()
    
