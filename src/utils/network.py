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
        self.id = None
        self.lobby_state = []
        self.room_num = None
        self.running = True
        self.kicked = False
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
        self.send(data)
        reply = self.client.recv(2048).decode()
        self.id = reply.split(":")[2]
        
        # Wait a moment for the initial lobby state
        import time
        time.sleep(0.1)
        
        # Try to receive initial lobby state
        try:
            self.client.settimeout(0.5)
            initial_data = self.client.recv(2048).decode()
            if initial_data and '{' in initial_data:
                message = json.loads(initial_data)
                if message.get("type") == "LobbyUpdate":
                    self.lobby_state = message["players"]
                    print("Initial Lobby State:", self.lobby_state)
            self.client.settimeout(None)  # Reset timeout
        except:
            self.client.settimeout(None)  # Reset timeout
            pass
            
        return reply

    def receive_room_list(self):
        try:
            data = self.client.recv(2048).decode()
            return json.loads(data)
        except:
            return []

    def start_lobby_listener(self):
        """Start the background thread for listening to lobby updates"""
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_for_updates, daemon=True)
            self.listener_thread.start()

    def stop_lobby_listener(self):
        """Stop the background thread"""
        self.running = False

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
                        self.kicked = True
                        buffer = buffer[len("Kicked"):]  # Clear 'Kicked' part
                        continue

                    elif buffer.startswith("Room Closed"):
                        print("Room has been closed by host.")
                        self.kicked = True  # Reuse the same logic to return to room screen
                        buffer = buffer[len("Room Closed"):]  # Clear it from buffer
                        continue

                    # ... JSON message handling (existing code) ...
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

    def listen_for_lobby_updates(self):
        """This method now just ensures the listener thread is running"""
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.start_lobby_listener()
