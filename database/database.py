import datetime


DATABASE_FILE = "chat_log.txt"


def store_message(username, message):
    with open(DATABASE_FILE, "a") as f:
        timestamp = datetime.datetime.now()
        f.write(f"{timestamp} | {username}: {message}\n")


def get_messages():
    try:
        with open(DATABASE_FILE, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        return []