# Database Repository Specifications

## expected schema.sql: 

-- LEVEL 1: AUTHENTICATION
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LEVEL 2: METADATA & RELATIONSHIPS
CREATE TABLE IF NOT EXISTS Chats (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_name TEXT NOT NULL,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES Users (user_id)
);

CREATE TABLE IF NOT EXISTS ChatMembers (
    chat_id INTEGER,
    user_id INTEGER,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (chat_id, user_id),
    FOREIGN KEY (chat_id) REFERENCES Chats (chat_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

-- LEVEL 3: MESSAGE HISTORY
CREATE TABLE IF NOT EXISTS Messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    sender_id INTEGER,
    message_text TEXT NOT NULL,
    msg_seq INTEGER NOT NULL, -- Logical ordering from server queue
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES Chats (chat_id),
    FOREIGN KEY (sender_id) REFERENCES Users (user_id)
);

## 1. message_repository.py (Person 1 - Level 3)
**Focus:** High-volume message history and sequence ordering.
- **Function:** `save_message(chat_id, sender_id, text, msg_seq)`.
- **Function:** `get_chat_history(chat_id)`.
- **Requirement:** Must use `msg_seq` provided by server queues to ensure ordering.

## 2. chat_repository.py (Person 2 - Level 2)
**Focus:** Chat metadata and user-to-chat relationships.
- **Function:** `create_chat(chat_name, creator_id)`.
- **Function:** `add_user_to_chat(chat_id, user_id)`.
- **Function:** `get_members(chat_id)`.

## 3. db_connection.py (Shared Environment)
```python
import sqlite3

def get_db_connection():
    """Returns a connection with WAL mode enabled for concurrency."""
    conn = sqlite3.connect("chat_app.db")
    conn.execute("PRAGMA journal_mode=WAL;")  # Improves read/write concurrency
    conn.row_factory = sqlite3.Row  # Allows access by column name
    return conn