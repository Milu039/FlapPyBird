import socket
import threading
import json
import time

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "26.189.170.88"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = "0"
        self.lobby_state = []
        self.room_num = None
        self.running = True
        self.kicked = False
        self.room_closed = False
        self.listener_thread = None

        try:
            self.client.connect(self.addr)
        except Exception as e:
            print("Failed to connect:", e)

    def send(self, data):
        try:
            self.client.send(data.encode())
        except Exception as e:
            print(f"Failed to send data: {e}")

    def send_receive_id(self, data):
        print(f"Sending to server: {data}")
        self.send(data)

        max_attempts = 5
        for attempt in range(max_attempts):
            reply = self.client.recv(2048).decode()
            print(f"Received from server (attempt {attempt + 1}): {reply}")

            if reply.startswith('['):
                print("Received room list instead of join response, retrying...")
                continue

            if "Joined:" in reply:
                try:
                    parts = reply.split(":")
                    if len(parts) >= 3:
                        self.id = parts[2]
                        self.room_num = parts[1]
                        time.sleep(0.1)

                        try:
                            self.client.settimeout(0.5)
                            initial_data = self.client.recv(2048).decode()
                            if initial_data and '{' in initial_data:
                                message = json.loads(initial_data)
                                if message.get("type") == "LobbyUpdate":
                                    self.lobby_state = message["players"]
                                    print("Initial Lobby State:", self.lobby_state)
                            self.client.settimeout(None)
                        except:
                            self.client.settimeout(None)
                            pass

                        return reply
                    else:
                        print(f"Unexpected reply format: {reply}")
                        self.id = "0"
                except Exception as e:
                    print(f"Error parsing reply: {e}")
                    self.id = "0"
                break

        print("Failed to get proper join response from server")
        self.id = "0"
        return reply

    def receive_room_list(self):
        try:
            data = self.client.recv(2048).decode()
            if data:
                return json.loads(data)
            return []
        except socket.timeout:
            return []
        except Exception as e:
            print(f"Error receiving room list: {e}")
            return []

    def start_lobby_listener(self):
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_for_updates, daemon=True)
            self.listener_thread.start()

    def stop_lobby_listener(self):
        self.running = False

    def handle_room_termination(self, reason="kicked"):
        self.running = False
        self.lobby_state = []
        self.room_num = None
        self.listener_thread = None
        if reason == "kicked":
            self.kicked = True
        elif reason == "closed":
            self.room_closed = True

    def _listen_for_updates(self):
        buffer = ""

        while self.running:
            try:
                self.client.settimeout(0.5)
                data = self.client.recv(2048).decode()

                if not data:
                    continue

                buffer += data

                while buffer:
                    if buffer.startswith("Kicked"):
                        print("[INFO] You were kicked from the room.")
                        self.handle_room_termination(reason="kicked")
                        buffer = buffer[6:]
                        continue

                    if buffer.startswith("Room Closed"):
                        try:
                            parts = buffer.split(":")
                            if len(parts) >= 2:
                                closed_room = parts[1].strip()
                                if closed_room == self.room_num:
                                    print(f"[INFO] Room '{closed_room}' was closed by host.")
                                    self.handle_room_termination(reason="closed")
                            buffer = buffer[len("Room Closed:" + closed_room):]
                        except Exception as e:
                            print("Error parsing Room Closed message:", e)
                            buffer = ""
                        continue

                    try:
                        if '{' in buffer:
                            start = buffer.index('{')
                            brace_count = 0
                            end_pos = start
                            for i in range(start, len(buffer)):
                                if buffer[i] == '{':
                                    brace_count += 1
                                elif buffer[i] == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end_pos = i + 1
                                        break

                            if brace_count == 0:
                                json_str = buffer[start:end_pos]
                                message = json.loads(json_str)

                                if message.get("type") == "LobbyUpdate":
                                    self.lobby_state = message["players"]
                                    print("Updated Lobby State:", self.lobby_state)
                                
                                # Remove processed message from buffer
                                buffer = buffer[end_pos:]
                            else:
                                break
                        else:
                            buffer = ""
                            break

                    except (json.JSONDecodeError, ValueError) as e:
                        next_start = buffer.find('{', 1)
                        if next_start != -1:
                            buffer = buffer[next_start:]
                        else:
                            buffer = ""

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error in lobby listener: {e}")
                break

    def listen_for_lobby_updates(self):
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.start_lobby_listener()
