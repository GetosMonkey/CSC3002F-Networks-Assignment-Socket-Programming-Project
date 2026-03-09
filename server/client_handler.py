from protocol import receive_packet, encode_packet
from database.database import (
    check_auth, register_user, append_message, 
    get_or_create_private_chat, get_chat_members, 
    get_chat_by_id, get_or_create_global_chat,
    get_user_by_username, add_user_to_chat, create_chat
)

def send_to_members(packet, member_usernames, sender_socket, authenticated_clients):
    """Delivers packets only to specific users who are currently online."""
    for client_socket, username in authenticated_clients.items():
        if username in member_usernames and client_socket != sender_socket:
            try:
                client_socket.sendall(packet)
            except:
                pass # The finally block handles removal on disconnect

def handle_client(connection_socket, addr, authenticated_clients):
    current_user = None
    
    try:
        while True:
            sequence_number, message_type, body = receive_packet(connection_socket)
            if sequence_number is None: break

            target_members = []
            display_msg = ""
            response_body = ""

            # 1. Authentication & Registration
            if body.startswith("Authenticate/"):
                _, username, password = body.split("/")
                if check_auth(username, password):
                    current_user = username
                    authenticated_clients[connection_socket] = username # CRITICAL: Map socket to user
                    response_body = "SUCCESS"
                else:
                    response_body = "FAILURE"

            elif body.startswith("NewUser/"):
                _, username, password = body.split("/")
                result = register_user(username, password)
                if result == "SUCCESS":
                    current_user = username
                    authenticated_clients[connection_socket] = username # CRITICAL: Map socket to user
                    response_body = "SUCCESS"
                else:
                    response_body = result # e.g., "USERNAME_EXISTS"

            # 2. Command Parsing (The simpler way)
            elif current_user:
                if body.startswith("/"):
                    parts = body.split(" ", 2)
                    cmd = parts[0].lower()

                    if cmd == "/pm" and len(parts) == 3:
                        target_user, content = parts[1], parts[2]
                        chat_id = get_or_create_private_chat(current_user, target_user)
                        if chat_id:
                            append_message(chat_id, current_user, content)
                            target_members = [target_user]
                            display_msg = f"[PM from {current_user}]: {content}"
                            response_body = f"Private message sent to {target_user}."
                        else:
                            response_body = f"User {target_user} not found."

                    elif cmd == "/group" and len(parts) == 3:
                        try:
                            gid = int(parts[1])
                            content = parts[2]
                            chat = get_chat_by_id(gid)
                            if chat and chat["chat_type"] == "group":
                                members = [dict(m)["username"] for m in get_chat_members(gid)]
                                if current_user in members:
                                    append_message(gid, current_user, content)
                                    target_members = members
                                    display_msg = f"[Group {gid} - {current_user}]: {content}"
                                    response_body = f"Message sent to group {gid}."
                                else:
                                    response_body = "You are not a member of this group."
                            else:
                                response_body = f"Group {gid} does not exist."
                        except ValueError:
                            response_body = "Invalid group ID."

                    elif cmd == "/create" and len(parts) >= 2:
                        chat_id = create_chat("group")
                        user = get_user_by_username(current_user)
                        add_user_to_chat(chat_id, user["user_id"])
                        response_body = f"Group created! ID: {chat_id}"

                    elif cmd == "/join" and len(parts) == 2:
                        try:
                            gid = int(parts[1])
                            user = get_user_by_username(current_user)
                            add_user_to_chat(gid, user["user_id"])
                            response_body = f"Joined group {gid}."
                        except:
                            response_body = "Could not join group."

                else:
                    # Global Chat Logic
                    global_id = get_or_create_global_chat()
                    append_message(global_id, current_user, body)
                    target_members = [dict(m)["username"] for m in get_chat_members(global_id)]
                    display_msg = f"{current_user}: {body}"
                    response_body = "Message sent to global chat."

            else:
                response_body = "Please login first."

            # 3. Final Transmission
            if display_msg and target_members:
                packet = encode_packet(sequence_number, "DATA", display_msg)
                send_to_members(packet, target_members, connection_socket, authenticated_clients)
            
            # Send ACK back to sender
            connection_socket.sendall(encode_packet(sequence_number, "ACK", response_body))

    finally:
        if connection_socket in authenticated_clients:
            del authenticated_clients[connection_socket] # Remove on disconnect
        connection_socket.close()