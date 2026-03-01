# Programs: 

## 1️⃣ TCP Server (Main Central Server)

Handles:
- Login / authentication
- Text messaging
- Chat validation
- Database writes
- Spawning threads for multiple clients

This is your most important file.

## 2️⃣ TCP Client

Handles:
- Connecting to server
- Sending login credentials
- Sending text messages
- Receiving text messages

## 3️⃣ UDP Streaming Module

Handles:
- P2P live streaming (or simulated image streaming)
- Sending UDP packets
- Receiving UDP packets
- Experimenting with packet loss

This can be:

Separate udp_stream_sender.py
Separate udp_stream_receiver.py
OR
Integrated into client later

## 4️⃣ Database Layer (Server-side module)

We need a basic database connection file with functions like:

- create_user()
- store_message()
- get_chat_messages()
- get_user_chats()

As well as a database itself, for the prototype this could simply be a csv file

## 5️⃣ Protocol / Header Module

Custom Header needs:
- encode_header()
- decode_header()
- message framing logic
- sequence number handling

This should be its own module.

# Workload split: 

## 👑 Member 1

Define project structure
Implement protocol header logic
Implement threading server skeleton
Merge branches
Oversee experiments

## 👤 Member 2

TCP Client
Login + messaging logic
Basic CLI interface
Test with server
Explanatory Video

## 👤 Member 3

UDP experiment module
Image transfer via UDP
Simulated packet loss
Write Experimental Notes
Documentation

# Github and git commit note: 

🌳 Step 1: Protect Main
Only initial commits and merge into main. No one works directly on main.

🌿 Step 2: Everyone Creates Feature Branches

Example:
git checkout -b feature-tcp-server
git checkout -b feature-tcp-client
git checkout -b feature-udp-stream

🌿 Step 3: Work On Separate Branches

Each member:
 - Commits only their own files
 - Pushes their branch

git add .
git commit -m "Implemented threaded TCP server skeleton"
git push origin feature-tcp-server

🌿 Step 4: Pull Request → Review → Merge

Once the process is at a checkpoint one of us can review pull requests, test locally, and merge into main.