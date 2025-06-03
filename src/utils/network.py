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
        self.id = "0"  # Initialize with default value instead of None
        self.lobby_state = []
        self.room_num = None
        self.running = True
        self.kicked = False
        self.room_closed = False
        self.connection_lost = False
        self.listener_thread = None

        try:
            self.client.connect(self.addr)
        except Exception as e:
            print("Failed to connect:", e)
            self.connection_lost = True

    def send(self, data):
        try:
            # Check if we should stop sending (kicked or connection lost)
            if hasattr(self, 'kicked') and self.kicked:
                return
            if hasattr(self, 'connection_lost') and self.connection_lost:
                return
                
            self.client.send(data.encode())
        except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
            print(f"Failed to send data: {e}")
            # Connection is broken, set a flag
            self.connection_lost = True
            # Don't re-raise the exception, just return

    def send_receive_id(self, data):
        print(f"Sending to server: {data}")
        self.send(data)
        
        # Keep trying to receive until we get the correct response
        max_attempts = 5
        for attempt in range(max_attempts):
            reply = self.client.recv(2048).decode()
            print(f"Received from server (attempt {attempt + 1}): {reply}")
            
            # Check if this is a room list response (JSON array)
            if reply.startswith('['):
                print("Received room list instead of join response, retrying...")
                continue
            
            # Check if this is the expected join/create response
            if "Joined:" in reply:
                # Parse the ID from the reply
                try:
                    parts = reply.split(":")
                    if len(parts) >= 3:
                        self.id = parts[2]
                        print(f"Parsed ID: {self.id}")
                        
                        # Set room number from the reply
                        if len(parts) >= 2:
                            self.room_num = parts[1]
                        
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
                    else:
                        print(f"Unexpected reply format: {reply}")
                        self.id = "0"  # Default ID
                except Exception as e:
                    print(f"Error parsing reply: {e}")
                    self.id = "0"  # Default ID
                break
        
        # If we didn't get a proper response, set defaults
        print("Failed to get proper join response from server")
        self.id = "0"
        return reply

    def receive_room_list(self):
        try:
            # Check if connection is lost
            if hasattr(self, 'connection_lost') and self.connection_lost:
                return []
                
            data = self.client.recv(2048).decode()
            if data:
                return json.loads(data)
            return []
        except socket.timeout:
            # Timeout is fine, just return empty list
            return []
        except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
            print(f"Error receiving room list: {e}")
            self.connection_lost = True
            return []
        except Exception as e:
            print(f"Error receiving room list: {e}")
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
        """Background thread method that continuously listens for updates"""
        buffer = ""
        
        while self.running:
            try:
                # Set a timeout so the thread can check self.running periodically
                self.client.settimeout(0.5)
                data = self.client.recv(2048).decode()
                
                if not data:
                    continue
                
                # Add new data to buffer
                buffer += data
                
                # Process complete messages in the buffer
                while buffer:
                    if buffer.startswith("Kicked"):
                        self.kicked = True
                        buffer = buffer[6:]  # Remove "Kicked" from buffer
                        # Stop the listener immediately when kicked
                        self.running = False
                        print("Received kick message, stopping listener")
                        return
                    
                    # Try to find a complete JSON message
                    try:
                        # Check if we have a complete JSON object
                        if '{' in buffer:
                            start = buffer.index('{')
                            # Try to parse from the start of JSON
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
                            
                            if brace_count == 0:  # We have a complete JSON object
                                json_str = buffer[start:end_pos]
                                message = json.loads(json_str)
                                
                                if message.get("type") == "LobbyUpdate":
                                    self.lobby_state = message["players"]
                                    print("Updated Lobby State:", self.lobby_state)
                                elif message.get("type") == "RoomClosed":
                                    print("Room has been closed by host")
                                    self.room_closed = True
                                    # Stop the listener when room is closed
                                    self.running = False
                                    return
                                
                                # Remove processed message from buffer
                                buffer = buffer[end_pos:]
                            else:
                                # Incomplete JSON, wait for more data
                                break
                        else:
                            # No JSON start found, clear any non-JSON data
                            buffer = ""
                            break
                            
                    except (json.JSONDecodeError, ValueError) as e:
                        # Don't print error for concatenated messages, just try to recover
                        # Try to recover by finding the next JSON start
                        next_start = buffer.find('{', 1)
                        if next_start != -1:
                            buffer = buffer[next_start:]
                        else:
                            buffer = ""
                        
            except socket.timeout:
                # Timeout is expected, just continue
                continue
            except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
                if self.running:  # Only print error if we're supposed to be running
                    print(f"Connection error in lobby listener: {e}")
                self.connection_lost = True
                break
            except Exception as e:
                if self.running:  # Only print error if we're supposed to be running
                    print(f"Error in lobby listener: {e}")
                break

    def listen_for_lobby_updates(self):
        """This method now just ensures the listener thread is running"""
        if self.listener_thread is None or not self.listener_thread.is_alive():
            self.start_lobby_listener()