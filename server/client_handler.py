import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocol import receive_packet, encode_packet  # type: ignore

def handle_client(connection_socket, addr):
    """
    Handles a single client connection.
    - Checks for Auth/NewUser commands.
    - Responds with "Coming soon!" for menu options.
    - Echos other messages.
    """
    while True:
        try:
            # 1. Receive the packet using the custom protocol
            sequence_number, message_type, body = receive_packet(connection_socket)
            
            # If receive_packet returns None, the connection was closed
            if sequence_number is None:
                break

            print(f"[{addr}] Received: {body}")

            # 2. Check for Authentication Commands
            if body.startswith("NewUser/") or body.startswith("Authenticate/"):
                # For now, we just acknowledge success
                response_body = "SUCCESS"
            
            # 3. Check for Menu Options (1, 2, 3, 4)
            elif body in ["1", "2", "3", "4"]:
                # Map the number to the feature name
                feature_map = {
                    "1": "Private Message",
                    "2": "Message Group",
                    "3": "Create New Group",
                    "4": "Join Group"
                }
                feature_name = feature_map.get(body, "Unknown Feature")
                
                # Respond with the "Coming soon" message
                response_body = f"{feature_name}: Coming soon! Returning to menu..."
            
            # 4. Default Echo
            else:
                response_body = f"Server received: {body}"
                
            # 5. Send the response back using the custom protocol
            response_packet = encode_packet(sequence_number, "ACK", response_body)
            connection_socket.sendall(response_packet)

        except Exception as e:
            print(f"Error with {addr}: {e}")
            break

    print(f"Connection closed: {addr}")
    connection_socket.close()