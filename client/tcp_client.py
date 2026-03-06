from socket import *
import threading

SERVER_HOST = "localhost"
SERVER_PORT = 12001

#________________________________________
# Function definitions
#________________________________________

def authenticate(username, password, client_socket):
    message_string = "Authenticate/" + username + "/" + password
    client_socket.send(message_string.encode())

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

def show_menu():
    print("\n-- Welcome to WhatsUp --")
    print("1. Login")
    print("2. Sign-up")
    print("q. Quit")
    reply = input("Select an option by number or q to quit: ")
    return reply

def show_commands():
    print("\n-- Command Pallete --")
    print("Follow the syntax for each command to execute automatically:")
    print("1. Private Message (Syntax: /pm <user> <message>)")
    print("2. Message Group (Syntax: /group <group_id> <message>)")
    print("3. Create New Group (Syntax: /create <group_name>)")
    print("4. Join Group (Syntax: /join <group_id>)")
    print("Type 'logout' to return to menu.")
    print("Type 'quit' to exit.")

def receive_messages(client_socket, stop_event):
    while not stop_event.is_set():
        try:
            client_socket.settimeout(1.0) # Check stop_event every second
            try:
                message = client_socket.recv(1024).decode().strip()
                if not message:
                    break
                # Print on a new line to avoid interfering with current input prompt
                print(f"\n{message}")
            except timeout:
                continue
        except:
            print("\nDisconnected from server.")
            break

#________________________________________
# Main Program
#________________________________________

def start_client():
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")
    except Exception as e:
        print(f"Could not connect to server: {e}")
        return

    stop_listener = threading.Event()

    while True: # Session reset loop
        authenticated = False
        
        # Phase 1: Authentication (Blocking)
        while not authenticated:
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

        # Phase 2: Start Background Thread (Only after authenticated)
        stop_listener.clear()
        listener_thread = threading.Thread(target=receive_messages, args=(client_socket, stop_listener))
        listener_thread.daemon = True # Ensure thread closes when main program exits
        listener_thread.start()

        print("\nAuthenticated successfully!")
        show_commands()

        # Phase 3: Command Loop (Main Thread)
        while True:
            message = input("> ")
            if message.lower() == "quit":
                client_socket.close()
                return
            
            if message.lower() == "logout":
                print("Logging out...")
                stop_listener.set() # Stop the background thread
                listener_thread.join() # Wait for it to exit
                client_socket.settimeout(None) # Reset blocking mode
                break # Return to authentication menu
            
            # In a real app, you might want to prepend the username or handle protocol formatting
            client_socket.send(message.encode())

if __name__ == "__main__":
    start_client()
