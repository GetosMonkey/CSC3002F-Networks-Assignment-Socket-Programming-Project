import hashlib
from .db_connection import get_connection

# --- User Functions ---

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        return cur.lastrowid
    except Exception:
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

# In database/database.py
def register_user(username, email, password):
    # 1. Specific check for existing user to give better feedback
    existing_user = get_user_by_username(username)
    if existing_user is not None:
        return "EXISTS" # Specific return for the handler to use

    password_hash = hash_password(password)
    user_id = create_user(username, email, password_hash)
    return "SUCCESS" if user_id else "FAILURE"

# --- Chat Functions ---

def create_chat(chat_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO chats (chat_type) VALUES (?)", (chat_type,))
    conn.commit()
    chat_id = cur.lastrowid
    conn.close()
    return chat_id

def add_user_to_chat(chat_id, user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO chat_members (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

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

def get_chat_members(chat_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.* FROM users u
        JOIN chat_members cm ON u.user_id = cm.user_id
        WHERE cm.chat_id = ?
        ORDER BY u.user_id ASC
    """, (chat_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_or_create_global_chat():
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
    
    # Local import to avoid circular dependency
    from server.message_queue import manager as queue_manager
    queue_manager.queue_message(actual_chat_id, sender_id, message)
    return True
