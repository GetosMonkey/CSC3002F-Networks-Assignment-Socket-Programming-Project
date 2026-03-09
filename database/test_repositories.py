import hashlib
import time

from .database import (
    create_user, get_user_by_username, verify_login,
    create_chat, add_user_to_chat, get_user_chats, get_chat_members,
    save_message, get_messages, get_recent_messages
)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def main():
    suffix = str(int(time.time()))

    username1 = f"alice_{suffix}"
    username2 = f"bob_{suffix}"

    password1 = hash_password("pass123")
    password2 = hash_password("pass456")

    print("Creating users...")
    user1_id = create_user(username1, f"{username1}@example.com", password1)
    user2_id = create_user(username2, f"{username2}@example.com", password2)

    print("user1_id =", user1_id)
    print("user2_id =", user2_id)

    print("\nFetching user by username...")
    user1 = get_user_by_username(username1)
    print(dict(user1) if user1 else None)

    print("\nVerifying login...")
    login_result = verify_login(username1, password1)
    print(dict(login_result) if login_result else None)

    print("\nCreating group chat...")
    chat_id = create_chat("group")
    print("chat_id =", chat_id)

    print("\nAdding users to chat...")
    print(add_user_to_chat(chat_id, user1_id))
    print(add_user_to_chat(chat_id, user2_id))

    print("\nGetting chats for user1...")
    chats = get_user_chats(user1_id)
    for chat in chats:
        print(dict(chat))

    print("\nGetting chat members...")
    members = get_chat_members(chat_id)
    for member in members:
        print(dict(member))

    print("\nSaving messages (via queue)...")
    save_message(chat_id, user1_id, "Hello Bob", 1)  # Manual for direct test
    save_message(chat_id, user2_id, "Hi Alice", 2)
    save_message(chat_id, user1_id, "How are you?", 3)

    print("\nFull chat history...")
    messages = get_messages(chat_id)
    for msg in messages:
        print(dict(msg))

    print("\nRecent messages...")
    recent = get_recent_messages(chat_id, limit=2)
    for msg in recent:
        print(dict(msg))


if __name__ == "__main__":
    main()
