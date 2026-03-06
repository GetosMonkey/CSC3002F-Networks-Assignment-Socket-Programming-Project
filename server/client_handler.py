from protocol import receive_packet, encode_packet  # type: ignore
from database.database import check_auth, register_user, append_message  # Added append_message

# right now sends a message to all clients except the sender (will change with db restrictions & auth in future)
def broadcast(message, sender_socket, clients):
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message)
            except:
                if client in clients:
                    clients.remove(client)

# Handles all client-server implementation acting as the logic behind all the buttons and actions of the frontend
def handle_client(connection_socket, addr, clients):
    current_user = None
    
    try:
        while True:
            try:
                sequence_number, message_type, body = receive_packet(connection_socket)
                
                if sequence_number is None:
                    break

                print(f"[{addr}] Received: {body}")

                # 1. Authentication/Login
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

                # 2. user registration/Signup
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
                
                # 3. Menu Options
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
                
                # 4. Broadcasting
                else:
                    if current_user:
                        broadcast_msg = f"{current_user}: {body}"
                        
                        # Broadcast to everyone else
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
