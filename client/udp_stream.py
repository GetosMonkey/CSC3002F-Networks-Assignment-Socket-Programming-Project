from socket import *
import threading

class UDPPeer:
    def __init__(self):
        self.sock = None
        self.listen_port = None
        self.current_peer = None  # (username, ip, port)
        self.running = False

    def start_listener(self, port: int):
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", port))
        self.listen_port = port
        self.running = True

        threading.Thread(target=self._receive_loop, daemon=True).start()
        print(f"[UDP] Listening for peer packets on port {port}")

    def _receive_loop(self):
        while self.running and self.sock is not None:
            try:
                data, addr = self.sock.recvfrom(4096)
                message = data.decode(errors="replace").strip()
                print(f"\n[UDP from {addr[0]}:{addr[1]}] {message}")
            except OSError:
                break
            except Exception as e:
                print(f"\n[UDP] Receive error: {e}")
                break

    def set_peer(self, username: str, ip: str, port: int):
        self.current_peer = (username, ip, port)
        print(f"[UDP] Current peer set to {username} at {ip}:{port}")

    def send(self, message: str):
        if self.sock is None:
            print("[UDP] Start a listener first with /udp-listen <port>")
            return
        if self.current_peer is None:
            print("[UDP] No peer selected. Use /udp-connect <username> first.")
            return

        username, ip, port = self.current_peer
        payload = message.encode()
        self.sock.sendto(payload, (ip, port))
        print(f"[UDP -> {username}] {message}")

    def close(self):
        self.running = False
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None