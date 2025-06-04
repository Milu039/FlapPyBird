import pygame
from ..utils import GameConfig
from .entity import Entity

class Skin(Entity):
    def __init__(self, config: GameConfig, player_id):
        super().__init__(config)
        self.skin_id = 0
        self.skin = config.images.skin[self.skin_id][0]
        self.unknow_skin = config.images.skin[4][0]
        self.player_id = player_id

    def next(self):
        self.skin_id = (self.skin_id + 1) % 4
        self.skin = self.config.images.skin[self.skin_id][0]

    def previous(self):
        self.skin_id = (self.skin_id - 1) % 4
        self.skin = self.config.images.skin[self.skin_id][0]
    
    def set_skin(self, skin_id):
        self.skin_id = skin_id
        self.skin = self.config.images.skin[skin_id][0]
    
    def get_skin_id(self):
        return self.skin_id

    def draw(self):
        posSkin = self.get_position_by_id(self.player_id)
        self.config.screen.blit(self.skin, posSkin)

        posSkin1 = self.get_position_by_id("1")
        self.config.screen.blit(self.unknow_skin, posSkin1)

        posSkin2 = self.get_position_by_id("2")
        self.config.screen.blit(self.unknow_skin, posSkin2)

        posSkin3 = self.get_position_by_id("3")
        self.config.screen.blit(self.unknow_skin, posSkin3)

    def draw_other(self, other_players):
        for player in other_players:
            pid = player["player_id"]
            skin_id = player["skin_id"]
            posSkin = self.get_position_by_id(pid)

            # Draw skin
            skin_img = self.config.images.skin[skin_id][0]
            self.config.screen.blit(skin_img, posSkin)

    def get_position_by_id(self, player_id):
        pos_map = {
            "0": (375, 215),
            "1": (600, 215),
            "2": (375, 375),
            "3": (600, 375)
        }
        return pos_map.get(str(player_id), (0, 0))
    
    def determine_rank(self,players):
        # Sort players by x (descending), then y (optional), and return the top one
        sorted_players = sorted(players, key=lambda p: p['x'], reverse=True)
        return sorted_players

    def draw_rank(self, other_players):
        ranked_players = self.determine_rank(other_players)

        # Podium drawing positions: (bird_x, bird_y, name_x, name_y)
        podium_positions = [
            (485, 285, 450, 340),  # 1st
            (345, 330, 305, 385),  # 2nd
            (630, 375, 590, 430),  # 3rd
            (485, 530, 445, 580),  # 4th
        ]

        font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 16)

        for i, player in enumerate(ranked_players):
            if i >= len(podium_positions):
                break

            bird_x, bird_y, name_x, name_y = podium_positions[i]
            skin_id = player["skin_id"]
            name = player["name"]

            # Get the skin image from the config
            if 0 <= skin_id < len(self.config.images.skin):
                skin_img = self.config.images.skin[skin_id][0]
                if i == 3:
                    skin_img = pygame.transform.rotate(skin_img, -180)
                self.config.screen.blit(skin_img, (bird_x, bird_y))

            # Draw the name
            name_surface = font.render(name, True, (0, 0, 0))
            self.config.screen.blit(name_surface, (name_x, name_y))

        
