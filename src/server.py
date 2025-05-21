import socket
import threading
import time

class FlappyServer:
    def __init__(self, host='0.0.0.0', port=5555, max_players=4):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.max_players = max_players
        
        # Player state format: "id:x,y,rotation"
        self.player_states = {}
        self.current_id = 0
        self.lock = threading.Lock()  # For thread-safe access to player_states
        
        try:
            self.server_socket.bind((self.host, self.port))
        except socket.error as e:
            print(f"Socket Bind Error: {e}")
            exit()
            
    def start(self):
        """Start the server, listening for connections"""
        self.server_socket.listen(self.max_players)
        print(f"Flappy Bird Server started on {self.host}:{self.port}")
        print(f"Waiting for connections... (Max players: {self.max_players})")
        
        try:
            while True:
                conn, addr = self.server_socket.accept()
                print(f"Connected to: {addr}")
                
                # Start a new thread to handle this client
                threading.Thread(target=self.client_handler, args=(conn,)).start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()
            
    def client_handler(self, conn):
        """Handle communication with a connected client"""
        # Assign player ID and initial position
        with self.lock:
            player_id = self.current_id
            self.current_id += 1
            # Initialize player with starting position at the center of screen
            # Format: "id:x,y,rotation"
            self.player_states[player_id] = f"{player_id}:200,300,0"
        
        # Send player ID to client
        conn.send(str.encode(str(player_id)))
        
        try:
            while True:
                data = conn.recv(2048)
                if not data:
                    break
                
                player_data = data.decode('utf-8')
                # Update this player's state
                with self.lock:
                    parts = player_data.split(':')
                    if len(parts) == 2:
                        pid = int(parts[0])
                        self.player_states[pid] = player_data
                
                # Create response with all other players' states
                response = []
                with self.lock:
                    for pid, state in self.player_states.items():
                        if pid != player_id:  # Don't send player their own state
                            response.append(state)
                
                # Send all other player states back
                conn.send(str.encode('|'.join(response)))
        except Exception as e:
            print(f"Error handling client {player_id}: {e}")
        finally:
            # Clean up when player disconnects
            with self.lock:
                if player_id in self.player_states:
                    del self.player_states[player_id]
            print(f"Player {player_id} disconnected")
            conn.close()

if __name__ == "__main__":
    server = FlappyServer()
    server.start()