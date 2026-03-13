from .database import (
    create_user, get_user_by_username,
    create_chat, add_user_to_chat, get_chat_by_name, get_chat_members
)
import time

def test_groups():
    suffix = str(int(time.time()))
    u1 = f"u1_{suffix}"
    p1 = "pass"
    
    print(f"Creating user {u1}...")
    uid1 = create_user(u1, p1)
    
    group_name = f"TestGroup_{suffix}"
    print(f"Creating group '{group_name}'...")
    gid = create_chat("group", name=group_name)
    print(f"Group ID: {gid}")
    
    print(f"Adding user to group...")
    add_user_to_chat(gid, uid1)
    
    print(f"Looking up group by name...")
    chat = get_chat_by_name(group_name)
    if chat and chat['chat_id'] == gid:
        print("SUCCESS: Group found by name correctly.")
    else:
        print(f"FAILURE: Group not found or ID mismatch. Found: {chat}")

    print(f"Checking members...")
    members = get_chat_members(gid)
    usernames = [m['username'] for m in members]
    if u1 in usernames:
        print(f"SUCCESS: User {u1} is a member.")
    else:
        print(f"FAILURE: User {u1} not found in members: {usernames}")

if __name__ == "__main__":
    test_groups()
