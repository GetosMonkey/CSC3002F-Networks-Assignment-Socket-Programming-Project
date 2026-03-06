import os

# Ensure database directory exists
if not os.path.exists("database"):
    os.makedirs("database")

# Verifies user by checking to see if username:password pair exists
def check_auth(username, password):
    if not os.path.exists("database/auth.txt"): return False
    with open("database/auth.txt", "r") as f:
        for line in f:
            if line.strip() == f"{username}:{password}":
                return True
    return False

# Creates a new username:password pair per new sign-up: in future this should only apply to unique usernames
def register_user(username, password):
    with open("database/auth.txt", "a") as f:
        f.write(f"{username}:{password}\n")

# Simulates queued/atomic write to global chat history
def append_message(chat_id, sender, message):
    filename = f"database/chat_{chat_id}.txt"
    with open(filename, "a") as f:
        f.write(f"{sender}:{message}\n")