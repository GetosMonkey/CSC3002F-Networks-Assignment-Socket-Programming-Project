import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from socket import *
import threading
import json
from protocol import receive_packet, encode_packet

SERVER_HOST = "localhost"
SERVER_PORT = 12001

def authenticate(username, password, client_socket):
    message_string = "Authenticate/" + username + "/" + password
    client_socket.sendall(encode_packet(0, "AUTH", message_string))

def display_history(data_json):
    try:
        data = json.loads(data_json)
        print("\n" + "="*40)
        print("       RECENT CHAT HISTORY")
        print("="*40)
        
        chats = data.get("chats", [])
        if not chats:
            print("  No recent activity.")
        
        for chat in chats:
            chat_name = f"Group {chat['chat_id']}"
            if chat['chat_type'] == 'private':
                members = chat.get('members', [])
                other_user = next((m for m in members if m != data['user']['username']), "Unknown")
                chat_name = f"PM with {other_user}"
            elif chat['chat_id'] == 1:
                chat_name = "Global Chat"
            
            print(f"\n>>> {chat_name} <<<")
            msgs = chat.get("recent_messages", [])
            if not msgs:
                print("  (Empty)")
            for msg in msgs:
                # database saves messages with sender_id. 
                # Since we don't have a full user mapping here, we show what we have.
                # In the future, we could include sender_name in the message object.
                print(f"  - {msg['content']}")
        print("\n" + "="*40 + "\n")
    except Exception as e:
        print(f"Error displaying history: {e}")

# Checks to see if the user is authenticated
def login(client_socket):
    username = input("Enter username: ")
    password = input("Enter password:  ")
    authenticate(username, password, client_socket)
    
    _, _, response = receive_packet(client_socket)
    if response and response.startswith("SUCCESS"):
        if "|" in response:
            _, data_json = response.split("|", 1)
            display_history(data_json)
        return True
    else:
        msg = response.split("|")[1] if response and "|" in response else (response or "Connection lost")
        print(f"Login failed! (Server said: {msg})")
        return False

# Captures the new user's details and sends it to the server for a SUCCESS-ful account creation
def sign_up(client_socket):
    username = input("Enter a new username: ")
    password = input("Enter a new password: ")
    message_string = "NewUser" + "/" + username + "/" + password
    client_socket.sendall(encode_packet(0, "AUTH", message_string))
    
    _, _, response = receive_packet(client_socket)
    if response and response.startswith("SUCCESS"):
        print("Sign-up successful!")
        if "|" in response:
            _, data_json = response.split("|", 1)
            display_history(data_json)
        return True
    else:
        msg = response.split("|")[1] if response and "|" in response else (response or "Connection lost")
        print(f"Sign-up failed: {msg}")
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
    print("1. Private Message (Syntax: /pm user message)")
    print("2. Message Group (Syntax: /group group_name message)")
    print("3. Create New Group (Syntax: /create group_name)")
    print("4. Join Group (Syntax: /join group_name)")
    print("5. Broadcast (Syntax: /broadcast message)")
    print("Type 'logout' to return to menu.")
    print("Type 'quit' to exit.")

# Continuously listens for messages from the server and prints them to the terminal
def receive_messages(client_socket, stop_event):
    while not stop_event.is_set():
        try:
            client_socket.settimeout(1.0) 
            _, _, message = receive_packet(client_socket)
            if message is None:
                # receive_packet returns None when connection is closed
                break
            if not message:
                continue
            
            # Only print newlines if it doesn't look like a direct confirmation
            prefix = "\n" if not message.startswith("CONFIRM:") else ""
            print(f"{prefix}<< {message}")
        except timeout:
            continue
        except Exception as e:
            print(f"\nDisconnected from server: {e}")
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
            
            if message.startswith("/"):
                # Proactively strip brackets to avoid server-side ambiguity, 
                # but keep the command structure intact.
                import re
                # This regex finds <text> and replaces it with text
                message = re.sub(r'<([^>]+)>', r'\1', message)
            
            client_socket.sendall(encode_packet(0, "DATA", message))

if __name__ == "__main__":
    start_client()
