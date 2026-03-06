import os

# Ensure database directory exists
if not os.path.exists("database"):
    os.makedirs("database")

def check_auth(username, password):
    if not os.path.exists("database/auth.txt"): return False
    with open("database/auth.txt", "r") as f:
        for line in f:
            if line.strip() == f"{username}:{password}":
                return True
    return False

def register_user(username, password):
    with open("database/auth.txt", "a") as f:
        f.write(f"{username}:{password}\n")

def append_message(chat_id, sender, message):
    """
    Simulates atomic writes by appending to a per-chat file.
    This effectively uses the file system as your message queue.
    """
    filename = f"database/chat_{chat_id}.txt"
    with open(filename, "a") as f:
        f.write(f"{sender}:{message}\n")