import pygame
from .network import Network
from ..entities.player import Player, PlayerMode

class RemotePlayer:
    """Represents a player connected remotely"""
    def __init__(self, config, player_id):
        self.config = config
        self.id = player_id
        # Use the first player image
        self.image = config.images.player[0]
        self.x = 200  # Default position
        self.y = 300
        self.rot = 0  # Default rotation
        self.visible = True
        
    def update(self, x, y, rot):
        """Update position and rotation"""
        self.x = int(x)
        self.y = int(y)
        self.rot = float(rot)
        
    def draw(self):
        """Draw the remote player on screen"""
        if not self.visible:
            return
            
        rotated_image = pygame.transform.rotate(self.image, self.rot)
        rotated_rect = rotated_image.get_rect(center=(self.x + rotated_image.get_width()//2, 
                                                      self.y + rotated_image.get_height()//2))
        self.config.screen.blit(rotated_image, rotated_rect)

class MultiplayerManager:
    """Manages multiplayer functionality"""
    def __init__(self, config, host="localhost"):
        self.config = config
        try:
            self.network = Network(host)
            self.player_id = int(self.network.id)
            self.connected = self.player_id >= 0
        except:
            self.connected = False
            self.player_id = -1
        
        self.remote_players = {}  # Dictionary of remote players by ID
        self.last_update = pygame.time.get_ticks()
        self.update_interval = 50  # Send update every 50ms (20 updates/sec)
        
    def is_connected(self):
        """Check if connected to server"""
        return self.connected
        
    def update(self, player):
        """Update local player position to server and get remote players"""
        current_time = pygame.time.get_ticks()
        
        # Only send updates at the specified interval
        if current_time - self.last_update > self.update_interval and player.mode == PlayerMode.NORMAL:
            self.last_update = current_time
            
            # Send local player data
            data = f"{self.player_id}:{player.x},{player.y},{player.rot}"
            response = self.network.send(data)
            
            if response:
                # Process remote player data
                self.process_remote_players(response)
                
    def process_remote_players(self, data):
        """Process data received from server about other players"""
        if not data:
            return
            
        # Split data into individual player states
        player_states = data.split('|')
        
        # Track which players we've seen in this update
        seen_players = set()
        
        for state in player_states:
            if not state:
                continue
                
            parts = state.split(':')
            if len(parts) != 2:
                continue
                
            player_id = int(parts[0])
            pos_data = parts[1].split(',')
            
            if len(pos_data) < 3:
                continue
                
            seen_players.add(player_id)
            
            # Create or update remote player
            if player_id not in self.remote_players:
                self.remote_players[player_id] = RemotePlayer(self.config, player_id)
                
            # Update position
            self.remote_players[player_id].update(
                int(pos_data[0]), 
                int(pos_data[1]),
                float(pos_data[2])
            )
        
        # Remove players that weren't in this update (disconnected)
        to_remove = []
        for pid in self.remote_players:
            if pid not in seen_players:
                to_remove.append(pid)
                
        for pid in to_remove:
            del self.remote_players[pid]
            
    def draw_remote_players(self):
        """Draw all remote players"""
        for player_id, player in self.remote_players.items():
            player.draw()