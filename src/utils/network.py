import socket
import threading
import json
import time

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "26.10.79.128"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = "0"
        self.lobby_state = []
        self.game_state = []
        self.room_num = None
        self.running = True
        self.kicked = False
        self.room_closed = False
        self.game_start = False
        self.restart = False
        self.pipe_callback = None
        self.timer_callback = None
        self.lobby_listener_thread = None
        self.game_listener_thread = None

        try:
            self.client.connect(self.addr)
            self.client.settimeout(0.5)  # Set initial timeout for recv
        except Exception as e:
            print("Failed to connect:", e)

    def send(self, data):
        try:
            #print(f"Sending: {data}")
            self.client.send(data.encode())
        except Exception as e:
            print(f"Failed to send data: {e}")

    def send_receive_id(self, data):
        print(f"Sending to server: {data}")
        self.send(data)

        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                reply = self.client.recv(2048).decode()
            except socket.timeout:
                print("Timeout waiting for reply...")
                continue
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
                            self.client.settimeout(0.5)
                        except Exception:
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
        return ""

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
        if self.lobby_listener_thread is None or not self.lobby_listener_thread.is_alive():
            self.running = True
            self.lobby_listener_thread = threading.Thread(target=self._listen_lobby_updates, daemon=True)
            self.lobby_listener_thread.start()

    def start_game_listener(self):
        if self.game_listener_thread is None or not self.game_listener_thread.is_alive():
            self.running = True
            self.game_listener_thread = threading.Thread(target=self._listen_game_updates, daemon=True)
            self.game_listener_thread.start()

    def stop_listeners(self):
        self.running = False
        if self.lobby_listener_thread:
            self.lobby_listener_thread.join(timeout=1)
            self.lobby_listener_thread = None
        if self.game_listener_thread:
            self.game_listener_thread.join(timeout=1)
            self.game_listener_thread = None

    def handle_room_termination(self, reason="kicked"):
        print(f"Handling room termination due to {reason}")
        self.running = False
        self.lobby_state = []
        self.room_num = None
        self.kicked = (reason == "kicked")
        self.room_closed = (reason == "closed")

    def _listen_lobby_updates(self):
        buffer = ""

        while self.running:
            try:
                data = self.client.recv(2048).decode()
                print(data)
                if not data:
                    continue

                buffer += data

                while buffer:
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)

                        if line.startswith("UpdateID:"):
                            # Extract ID part only
                            id_part = line.split(":")[1]
                            if "{" in id_part:
                                id_part, leftover = id_part.split("{", 1)
                                buffer = "{" + leftover + "\n" + buffer  # Put JSON back into buffer
                            try:
                                self.id = int(id_part.strip())
                                print(f"[INFO] Updated player ID to {self.id}")
                            except ValueError:
                                print("[ERROR] Invalid ID received.")

                        elif line == "Kicked":
                            print("[INFO] You were kicked from the room.")
                            self.handle_room_termination(reason="kicked")
                            continue

                    # Any leftover non-line-based commands (like Start, Restart)
                    if buffer.startswith("Start"):
                        print("[INFO] Host has started the game.")
                        self.game_start = True
                        buffer = buffer[len("Start"):]
                        continue

                    if buffer.startswith("Restart"):
                        print("[INFO] Restart command received. Returning to Room Lobby.")
                        self.restart = True
                        buffer = buffer[len("Restart"):]
                        continue


                    # Process JSON messages
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
                            try:
                                message = json.loads(json_str)
                                if message.get("type") == "LobbyUpdate":
                                    self.lobby_state = message["players"]
                                    print("Lobby Update:", self.lobby_state)
                                elif message.get("type") == "RoomClosed":
                                    print("[INFO] Room was closed by host.")
                                    self.handle_room_termination(reason="closed")
                            except Exception as e:
                                print(f"Error parsing JSON message: {e}")
                            buffer = buffer[end_pos:]
                        else:
                            break
                    else:
                        buffer = ""
                        break

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error in lobby listener: {e}")
                break

        print("[INFO] Lobby listener stopped.")

    def _listen_game_updates(self):
        buffer = ""

        while self.running:
            try:
                data = self.client.recv(2048).decode()
                if not data:
                    continue

                buffer += data

                while buffer:
                    if buffer.startswith("GetFrozen:"):
                        # Extract who used the freeze skill
                        freeze_user = int(buffer.split(":")[1])
                        print(f"[INFO] Got frozen by player {freeze_user}")
                        
                        # Set freeze state on THIS player
                        self.freeze_active = True
                        self.freeze_start_time = time.time()
                        
                        # Remove the processed command from buffer
                        buffer = buffer[len("GetFrozen:"):].split(":", 1)[-1] if ":" in buffer else ""
                        continue
                    
                    if buffer.startswith("TeleportTo:"):
                        parts = buffer.split(":")
                        if len(parts) >= 3:
                            new_x = float(parts[1])
                            new_y = float(parts[2])
                            print(f"[INFO] Received teleport to ({new_x}, {new_y})")
                            
                            self.teleport_active = True
                            self.teleport_x = new_x
                            self.teleport_y = new_y
                            
                            buffer = buffer[len(f"TeleportTo:{new_x}:{new_y}"):].lstrip(":")
                            continue
                    
                    if buffer.startswith("AllReady"):
                        print("[INFO] All players are ready.")
                        self.all_ready = True
                        buffer = buffer[len("AllReady"):]
                        continue

                    if buffer.startswith("Pipe:"):
                        try:
                            parts = buffer.strip().split(":")
                            if len(parts) >= 3:
                                gap_y = int(parts[2])
                                # Only spawn pipe if this is NOT player 1
                                if self.id != "0":
                                    if hasattr(self, "pipe_callback") and self.pipe_callback:
                                        self.pipe_callback(gap_y)
                                # Trim the message to avoid duplication
                                buffer = ""
                                continue
                        except Exception as e:
                            print(f"Failed to handle pipe spawn: {e}")
                            buffer = ""
                            continue

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
                            try:
                                message = json.loads(json_str)
                                if message.get("type") == "GameUpdate":
                                    self.game_state = message["players"]
                                    print("Game Update:", self.game_state)
                            except Exception as e:
                                print(f"Error parsing JSON message: {e}")
                            buffer = buffer[end_pos:]
                        else:
                            break
                    else:
                        buffer = ""
                        break

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error in game listener: {e}")
                break

        print("[INFO] Game listener stopped.")

    def listen_for_lobby_updates(self):
        self.start_lobby_listener()

    def listen_for_game_updates(self):
        self.start_game_listener()

    def disconnect(self):
        self.running = False
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
