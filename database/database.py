import hashlib
from .db_connection import get_connection

# --- User Functions ---

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"Error creating user: {e}")  # ← Add this for debugging
        return None
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def verify_login(username, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    row = cur.fetchone()
    conn.close()
    return row

def check_auth(username, password_hash):
    return verify_login(username, password_hash)

def delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0

def check_auth(username, password):
    password_hash = hash_password(password)
    user = verify_login(username, password_hash)
    return user is not None

def register_user(username, password):
    existing_user = get_user_by_username(username)
    if existing_user is not None:
        return False
    password_hash = hash_password(password)
    user_id = create_user(username, password_hash)
    return user_id is not None

# --- Chat Functions ---

def create_chat(chat_type, name=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO chats (chat_type) VALUES (?)", (chat_type, name))
    conn.commit()
    chat_id = cur.lastrowid
    conn.close()
    return chat_id

def add_user_to_chat(chat_id, user_id):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO chat_members (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
        conn.commit()
    except:
        pass # If it fails (like a duplicate user), just ignore it and move on
    finally:
        conn.close()
    return True

def get_user_chats(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.* FROM chats c
        JOIN chat_members cm ON c.chat_id = cm.chat_id
        WHERE cm.user_id = ?
        ORDER BY c.chat_id ASC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_chat_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chats WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return row

def get_chat_members(chat_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.username FROM users u
        JOIN chat_members cm ON u.user_id = cm.user_id
        WHERE cm.chat_id = ?
        ORDER BY u.user_id ASC
    """, (chat_name,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_chat_by_id(chat_id):
    """Fetches details of a specific chat."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_chat_by_name(name):
    """Fetches details of a specific chat by its name."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chats WHERE name = ? AND chat_type = 'group'", (name,))
    row = cur.fetchone()
    conn.close()
    return row

def get_or_create_global_chat():
    """Simple helper for the global channel (Assuming ID 1 is Global)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM chats WHERE chat_type = 'group' ORDER BY chat_id ASC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row is not None:
        return row["chat_id"]
    return create_chat("group")

# --- Message Functions ---

def save_message(chat_id, sender_id, content, sequence_number, message_type="text"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO messages (chat_id, sender_id, message_type, content, sequence_number)
        VALUES (?, ?, ?, ?, ?)
    """, (chat_id, sender_id, message_type, content, sequence_number))
    conn.commit()
    conn.close()
    return sequence_number

def get_last_sequence(chat_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(sequence_number), 0) FROM messages WHERE chat_id = ?", (chat_id,))
    result = cur.fetchone()[0]
    conn.close()
    return result

def get_messages(chat_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY sequence_number ASC", (chat_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_recent_messages(chat_id, limit=20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM messages WHERE chat_id = ?
        ORDER BY sequence_number DESC LIMIT ?
    """, (chat_id, limit))
    rows = cur.fetchall()
    conn.close()
    return list(reversed(rows))

def append_message(chat_id, sender, message):
    user = get_user_by_username(sender)
    if user is None:
        return False
    
    sender_id = user["user_id"]

    if chat_id == "global":
        actual_chat_id = get_or_create_global_chat()
    else:
        actual_chat_id = int(chat_id)

    next_seq = get_last_sequence(actual_chat_id) + 1
    save_message(actual_chat_id, sender_id, message, next_seq)
    return True


def update_user_port(username, port):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET port_number = ? WHERE username = ?",
        (port, username)
    )
    conn.commit()
    conn.close()


def get_user_port(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT port_number FROM users WHERE username = ?",
        (username,)
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return row["port_number"]

    # Local import to avoid circular dependency
    from server.message_queue import manager as queue_manager
    queue_manager.queue_message(actual_chat_id, sender_id, message)
    return True

def get_or_create_private_chat(username1, username2):
    """Finds an existing DM between two users or creates one."""
    user1 = get_user_by_username(username1)
    user2 = get_user_by_username(username2)
    if not user1 or not user2: return None

    conn = get_connection()
    cur = conn.cursor()
    # Check for existing private chat between these two
    cur.execute("""
        SELECT cm1.chat_id FROM chat_members cm1
        JOIN chat_members cm2 ON cm1.chat_id = cm2.chat_id
        JOIN chats c ON cm1.chat_id = c.chat_id
        WHERE c.chat_type = 'private' AND cm1.user_id = ? AND cm2.user_id = ?
    """, (user1['user_id'], user2['user_id']))
    
    row = cur.fetchone()
    conn.close()

    if row:
        return row['chat_id']
    else:
        # Create new private chat
        # Set name to target user's username as per request
        new_id = create_chat('private', name=username2)
        add_user_to_chat(new_id, user1['user_id'])
        add_user_to_chat(new_id, user2['user_id'])
        return new_id

def get_all_groups():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT chat_id, name FROM chats WHERE chat_type = 'group'")
    rows = cur.fetchall()
    conn.close()
    return rows
