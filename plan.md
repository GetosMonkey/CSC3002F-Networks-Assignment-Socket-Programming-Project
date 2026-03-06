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

## 5th of March 2026 checkpoint: 

Report
2 minutes ago

Review
Codebase Analysis & Week 2 Requirements Check
Based on your current codebase, here is an explanation of what your code does right now, along with a comparison against the Week 2 project requirements.

What Your Code Does Right Now
Currently, your project consists of several disconnected pieces of code that do not yet form a cohesive application:

1. TCP Client & Server (The 
protocol.py
 Implementation)
server/tcp_server.py
: A multi-threaded TCP server listening on port 12000. It properly utilizes 
protocol.py
 to expect a strictly formatted message header (4-byte sequence number + 4-byte content length) before reading the message body.
client/tcp_client.py
: A simple TCP client that connects to port 12000 and sends user input.
⚠️ Critical Flaw: The TCP client does not use 
protocol.py
 (it just sends message.encode()). Because the server expects the 8-byte header and the client doesn't send it, the server will either hang while waiting for bytes or improperly parse the first 8 characters of your text message as a header, breaking the connection.
2. Group Chat Server & Client (The NICK Implementation)
server/server.py
 & 
server/client.py
: This appears to be a separate attempt at building a group chat using a simple NICK protocol for usernames.
⚠️ Critical Flaws: Neither file will run due to syntax errors:
In 
server.py
: server.blind((host, port)) should be server.bind(...).
In 
server.py
: client.append(client) should be clients.append(client).
In 
client.py
: client.side(message.encode('ascii')) should be client.send(...).
3. UDP Components
experiments/udp_test.py
 & 
client/udp_stream.py
: A basic UDP echo server that receives a message, converts it to uppercase, and sends it back. This works as a basic proof of concept for UDP sockets but does not implement the media streaming mentioned in your 
plan.md
.
4. Experiments & Plan
experiments/packet_loss_sim.py
: Contains a single function 
should_drop_packet
 to simulate network unreliability.
plan.md
: Outlines a solid architecture and team workload split, but the codebase has not yet caught up to the plan.
Comparison to Week 2 Requirements
For Stage 2 (Week 2), you are expected to deliver a prototype, a demo video, experimental notes, a technical reflection, and a GenAI declaration. Here is where you stand:

Deliverables Status
❌ 1. Prototype source code: Your code is currently fragmented and has syntax errors. You do not yet have a working prototype that fulfills the core features.
❌ 2. Demonstration video (≤ 5 mins): Cannot be recorded until the prototype is functional.
❌ 3. Experimental notes: The 
experiments/notes.md
 file is completely empty.
❌ 4. Technical reflection: Missing.
❌ 5. GenAI usage declaration: Missing.
Functional Requirements (For the Prototype)
⚠️ TCP and UDP: Both are started, but they exist as separate scripts rather than a unified application.
⚠️ Client–Server & P2P: You have Client-Server elements, but Peer-to-Peer (P2P) communication is completely missing.
✅ Raw Sockets: You are correctly using raw sockets (socket.socket).
⚠️ Concurrency: You are correctly using threading, but it is currently attached to the broken 
server/server.py
 and 
server/tcp_server.py
.
❌ User Identification: Attempted in 
server/server.py
 but currently broken due to syntax errors.
❌ One-to-One Chat: Not implemented.
❌ Group Chat: Attempted in 
server/server.py
 but non-functional.
❌ Media Transfer: Not implemented (only text is being sent).
Recommended Next Steps
To get your prototype ready for Week 2, I recommend tackling the following:

Fix the Syntax Errors: Fix the typos in 
server/server.py
 and 
server/client.py
 so they can actually run.
Unify the TCP Logic: Decide whether you are using the 
protocol.py
 header approach or the simple text-based NICK approach, and make sure both your client and server use the exact same logic. Currently, they are incompatible.
Add P2P / UDP Media: Implement the UDP streaming module mentioned in your plan to satisfy the UDP, P2P, and Media transfer requirements.
Draft the Notes: Since you have the 
packet_loss_sim.py
 snippet, you can start running tests with UDP packet loss and write up your findings in 
experiments/notes.md
.   

# Conflicts and merge errors: 

The Server [WinError 10048] error: You were getting "Only one usage of each socket address is normally permitted" because a previous run of the TCP server was still lingering in the background and holding port 12000 open. I found the hidden process causing the blockage using the terminal and killed it. 

tcp_server.py
 is now successfully running in the background again on your machine.

The Client Syntax errors: Your friend's merge brought in a few syntax typos in 

client/tcp_client.py
 which I have corrected:

1024.decode was trying to run the .decode() string method on the integer 1024 instead of the socket's output. I corrected this to recv(1024).decode().
if response ="SUCCESS": was missing the second equals sign (==) required for comparison, which I added.
else authenticated =False was missing a colon line break, which I added.

sign_up
 was trying to return a variable named valid that hadn't been defined, so I changed the response handler to return True or False instead.

main()
 was missing the call to actually start the client, which I uncommented.