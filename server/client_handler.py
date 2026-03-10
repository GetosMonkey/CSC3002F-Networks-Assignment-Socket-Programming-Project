from protocol import receive_packet, encode_packet
from database.database import (
    check_auth, register_user, append_message, 
    get_or_create_private_chat, get_chat_members, 
    get_chat_by_id, get_or_create_global_chat,
    get_user_by_username, add_user_to_chat, create_chat
)

import json
from db_handler import handle_login, handle_register

def send_to_members(packet, member_usernames, sender_socket, authenticated_clients, include_sender=False):
    """Delivers packets only to specific users who are currently online."""
    for client_socket, username in authenticated_clients.items():
        if username in member_usernames:
            if not include_sender and client_socket == sender_socket:
                continue
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
            include_sender_in_broadcast = False

            # 1. Authentication & Registration
            if body.startswith("Authenticate/"):
                parts = body.split("/")
                if len(parts) == 3:
                    _, username, password = parts
                    result = handle_login(username, password)
                    if result["status"] == "SUCCESS":
                        current_user = username
                        authenticated_clients[connection_socket] = username
                        
                        # Ensure user is in global chat (ID 1)
                        user_info = get_user_by_username(username)
                        add_user_to_chat(1, user_info["user_id"])
                        
                        # Return history as JSON after the SUCCESS flag
                        response_body = "SUCCESS|" + json.dumps(result)
                    else:
                        response_body = "FAILURE|" + result["message"]
                else:
                    response_body = "FAILURE|Invalid format"

            elif body.startswith("NewUser/"):
                parts = body.split("/")
                if len(parts) == 3:
                    _, username, password = parts
                    result = handle_register(username, password)
                    if result["status"] == "SUCCESS":
                        current_user = username
                        authenticated_clients[connection_socket] = username
                        response_body = "SUCCESS|" + json.dumps(result)
                    else:
                        response_body = "FAILURE|" + result["message"]
                else:
                    response_body = "FAILURE|Invalid format"

            # 2. Command Parsing (The robust way)
            elif current_user:
                if body.startswith("/"):
                    parts = body.split(" ", 2)
                    cmd = parts[0].lower()

                    if cmd == "/pm" and len(parts) >= 2:
                        # Improved PM parsing to handle possible <> or lack thereof
                        cmd_line = body[len(cmd):].strip()
                        if cmd_line.startswith("<"):
                            target_user = cmd_line[1:cmd_line.find(">")].strip()
                            content = cmd_line[cmd_line.find(">")+1:].strip()
                        else:
                            pm_parts = cmd_line.split(" ", 1)
                            target_user = pm_parts[0]
                            content = pm_parts[1] if len(pm_parts) > 1 else ""
                        
                        chat_id = get_or_create_private_chat(current_user, target_user)
                        if chat_id:
                            append_message(chat_id, current_user, content)
                            target_members = [target_user, current_user]
                            display_msg = f"[PM with {target_user}]: {content}"
                            response_body = "PM sent."
                            include_sender_in_broadcast = True
                        else:
                            response_body = f"User {target_user} not found."

                    elif cmd == "/group" and len(parts) >= 2:
                        # Support /group <id_or_name> <message>
                        cmd_line = body[len(cmd):].strip()
                        group_target = ""
                        content = ""
                        
                        if cmd_line.startswith("<"):
                            group_target = cmd_line[1:cmd_line.find(">")].strip()
                            content = cmd_line[cmd_line.find(">")+1:].strip()
                        else:
                            group_parts = cmd_line.split(" ", 1)
                            group_target = group_parts[0]
                            content = group_parts[1] if len(group_parts) > 1 else ""

                        chat = None
                        try:
                            gid = int(group_target)
                            chat = get_chat_by_id(gid)
                        except ValueError:
                            chat = get_chat_by_name(group_target)

                        if chat and chat["chat_type"] == "group":
                            gid = chat["chat_id"]
                            members = [m["username"] for m in get_chat_members(gid)]
                            if current_user in members:
                                append_message(gid, current_user, content)
                                target_members = members
                                display_msg = f"[Group {chat['name'] or gid} - {current_user}]: {content}"
                                response_body = "Group message sent."
                                include_sender_in_broadcast = True
                            else:
                                response_body = "You are not a member of this group."
                        else:
                            response_body = f"Group '{group_target}' does not exist."

                    elif cmd == "/create" and len(parts) >= 2:
                        group_name = body[len(cmd):].strip().strip("<> ")
                        chat_id = create_chat("group", name=group_name)
                        user = get_user_by_username(current_user)
                        add_user_to_chat(chat_id, user["user_id"])
                        response_body = f"CONFIRM: Group '{group_name}' created successfully!"

                    elif cmd == "/join" and len(parts) >= 2:
                        group_target = body[len(cmd):].strip().strip("<> ")
                        chat = None
                        try:
                            # Still allow ID if they happen to know it, but logic should prefer name
                            gid = int(group_target)
                            chat = get_chat_by_id(gid)
                        except ValueError:
                            chat = get_chat_by_name(group_target)
                        
                        if chat:
                            user = get_user_by_username(current_user)
                            add_user_to_chat(chat["chat_id"], user["user_id"])
                            name_display = chat['name'] if chat['name'] else f"ID {chat['chat_id']}"
                            response_body = f"CONFIRM: Joined group '{name_display}'."
                        else:
                            response_body = f"Group '{group_target}' not found."

                    elif cmd == "/broadcast":
                        content = body[len(cmd):].strip()
                        target_members = list(authenticated_clients.values())
                        display_msg = f"[BROADCAST from {current_user}]: {content}"
                        response_body = "Broadcast sent."
                        include_sender_in_broadcast = True

                    else:
                        response_body = f"Unknown command: {cmd}"

                else:
                    # Global Chat Logic
                    global_id = get_or_create_global_chat()
                    append_message(global_id, current_user, body)
                    # For global chat, target all online users
                    target_members = list(authenticated_clients.values())
                    display_msg = f"{current_user}: {body}"
                    response_body = "Global message sent."
                    include_sender_in_broadcast = True

            else:
                response_body = "Please login first."

            # 3. Final Transmission
            if display_msg and target_members:
                packet = encode_packet(sequence_number, "DATA", display_msg)
                send_to_members(packet, target_members, connection_socket, authenticated_clients, include_sender=include_sender_in_broadcast)
            
            # Send ACK back to sender
            if response_body:
                connection_socket.sendall(encode_packet(sequence_number, "ACK", response_body))

    finally:
        if connection_socket in authenticated_clients:
            del authenticated_clients[connection_socket] # Remove on disconnect
        connection_socket.close()