from protocol import receive_packet, encode_packet  # type: ignore
from database.database import check_auth, register_user, append_message  # Added append_message

def broadcast(message, sender_socket, clients):
    """Sends a message to all clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message)
            except:
                if client in clients:
                    clients.remove(client)

def handle_client(connection_socket, addr, clients):
    """
    Handles a single client connection.
    - Integrates with database for Auth/NewUser commands.
    - Manages global broadcast for authenticated users.
    """
    current_user = None
    
    try:
        while True:
            try:
                sequence_number, message_type, body = receive_packet(connection_socket)
                
                if sequence_number is None:
                    break

                print(f"[{addr}] Received: {body}")

                # 1. Handle Authentication (Authenticate/username/password)
                if body.startswith("Authenticate/"):
                    parts = body.split("/")
                    if len(parts) == 3:
                        _, username, password = parts
                        if check_auth(username, password):
                            current_user = username
                            print(f"[AUTH] Login successful for user: '{username}'")
                            response_body = "SUCCESS"
                            if connection_socket not in clients:
                                clients.append(connection_socket)
                        else:
                            print(f"[AUTH] Login failed for user: '{username}'")
                            response_body = "FAILURE"
                    else:
                        response_body = "INVALID_AUTH_FORMAT"

                # 2. Handle New User Registration (NewUser/username/password)
                elif body.startswith("NewUser/"):
                    parts = body.split("/")
                    if len(parts) == 3:
                        _, username, password = parts
                        register_user(username, password)
                        current_user = username
                        print(f"[DATABASE] User '{username}' was written to auth.txt")
                        response_body = "SUCCESS"
                        if connection_socket not in clients:
                            clients.append(connection_socket)
                    else:
                        response_body = "INVALID_SIGNUP_FORMAT"
                
                # 3. Handle Menu options (1, 2, 3, 4)
                elif body in ["1", "2", "3", "4"]:
                    feature_map = {
                        "1": "Private Message",
                        "2": "Message Group",
                        "3": "Create New Group",
                        "4": "Join Group"
                    }
                    feature_name = feature_map.get(body, "Unknown Feature")
                    print(f"[FEATURE] Mapping command '{body}' to: {feature_name}")
                    response_body = f"{feature_name}: Feature coming soon!"
                
                # 4. Global Broadcast (Default)
                else:
                    if current_user:
                        # Prepend username for identity-awareness
                        broadcast_msg = f"{current_user}: {body}"
                        
                        # Broadcast to everyone else
                        # Note: encode_packet adds the necessary newline
                        packet = encode_packet(sequence_number, "DATA", broadcast_msg)
                        broadcast(packet, connection_socket, clients)
                        
                        # Save to history
                        append_message("global", current_user, body)
                        
                        response_body = f"Message broadcasted to chat."
                    else:
                        response_body = "Please login first to chat."
                    
                # 5. Send ACK to the sender
                response_packet = encode_packet(sequence_number, "ACK", response_body)
                connection_socket.sendall(response_packet)

            except Exception as e:
                print(f"Error with {addr}: {e}")
                break
    finally:
        if connection_socket in clients:
            clients.remove(connection_socket)
        print(f"Connection closed: {addr}")
        connection_socket.close()
