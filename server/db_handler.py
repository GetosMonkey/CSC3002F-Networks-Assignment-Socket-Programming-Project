from database.database import (
    get_user_by_username, create_user, verify_login, hash_password,
    get_user_chats, get_chat_members, get_recent_messages,
    get_or_create_global_chat, add_user_to_chat, append_message
)

def handle_register(username, password):
    """Handle user registration with proper error messages"""
    # Check if username exists
    existing_user = get_user_by_username(username)
    if existing_user:
        return {
            "status": "USERNAME_EXISTS",
            "message": "Username already exists. Please choose another."
        }
    
    # Create user
    password_hash = hash_password(password)
    user_id = create_user(username, password_hash)
    
    if user_id:
        # Auto-join global chat
        global_chat_id = get_or_create_global_chat()
        add_user_to_chat(global_chat_id, user_id)
        
        return {
            "status": "SUCCESS",
            "user_id": user_id,
            "username": username,
            "message": "Registration successful!"
        }
    else:
        return {
            "status": "FAILURE",
            "message": "Registration failed due to server error."
        }

def handle_login(username, password):
    """Handle user login and load their data"""
    password_hash = hash_password(password)
    user = verify_login(username, password_hash)
    
    if not user:
        return {
            "status": "FAILURE",
            "message": "Invalid username or password."
        }
    
    # Get user's chats for loading initial data
    chats = get_user_chats(user["user_id"])
    chat_list = []
    
    for chat in chats:
        recent_msgs = get_recent_messages(chat["chat_id"], limit=20)
        members = get_chat_members(chat["chat_id"])
        
        chat_list.append({
            "chat_id": chat["chat_id"],
            "chat_type": chat["chat_type"],
            "recent_messages": [dict(msg) for msg in recent_msgs],
            "members": [dict(m)["username"] for m in members]
        })
    
    return {
        "status": "SUCCESS",
        "user": dict(user),
        "chats": chat_list,
        "message": "Login successful!"
    }

def handle_message(chat_id, sender_username, content):
    """Handle sending a message"""
    result = append_message(chat_id, sender_username, content)
    
    if result:
        return {
            "status": "SUCCESS",
            "message": "Message sent."
        }
    else:
        return {
            "status": "FAILURE",
            "message": "Failed to send message."
        }