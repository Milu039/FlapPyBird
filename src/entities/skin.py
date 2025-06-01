import pygame
from ..utils import GameConfig
from .entity import Entity

class Skin(Entity):
    def __init__(self, config: GameConfig, player_id):
        super().__init__(config)
        self.skin_id = 0
        self.skin = config.images.skin[self.skin_id]
        self.player_id = player_id

    def next(self):
        self.skin_id = (self.skin_id + 1) % 4
        self.skin = self.config.images.skin[self.skin_id]

    def previous(self):
        self.skin_id = (self.skin_id - 1) % 4
        self.skin = self.config.images.skin[self.skin_id]
    
    def get_skin_id(self):
        return self.skin_id

    def draw(self):
        posSkin = self.get_position_by_id(self.player_id)
        self.config.screen.blit(self.skin, posSkin)

    def draw_other(self, other_players):
        for player in other_players:
            pid = player["player_id"]
            skin_id = player["skin_id"]
            posSkin = self.get_position_by_id(pid)

            # Draw skin
            skin_img = self.config.images.skin[skin_id]
            self.config.screen.blit(skin_img, posSkin)

    def get_position_by_id(self, player_id):
        pos_map = {
            "0": (375, 215),
            "1": (600, 215),
            "2": (375, 375),
            "3": (600, 375)
        }
        return pos_map.get(str(player_id), (0, 0))