import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocol import receive_packet, encode_packet  # type: ignore
from database.database import check_auth, register_user  # Import database functions

def handle_client(connection_socket, addr):
    """
    Handles a single client connection.
    - Integrates with database for Auth/NewUser commands.
    - Responds with feature mappings for simple commands.
    """
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
                        response_body = "SUCCESS"
                    else:
                        response_body = "FAILURE"
                else:
                    response_body = "INVALID_AUTH_FORMAT"

            # 2. Handle New User Registration (NewUser/username/password)
            elif body.startswith("NewUser/"):
                parts = body.split("/")
                if len(parts) == 3:
                    _, username, password = parts
                    # We could check if user exists, but register_user currently just appends
                    register_user(username, password)
                    response_body = "SUCCESS"
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
                response_body = f"{feature_name}: Feature coming soon!"
            
            # 4. Default Echo
            else:
                response_body = f"Server received: {body}"
                
            response_packet = encode_packet(sequence_number, "ACK", response_body)
            connection_socket.sendall(response_packet)

        except Exception as e:
            print(f"Error with {addr}: {e}")
            break

    print(f"Connection closed: {addr}")
    connection_socket.close()
