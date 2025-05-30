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
        self.skin_id += 1
        if self.skin_id == 3:
            self.skin_id = 0
            self.skin = self.config.images.skin[self.skin_id]
        else:
            self.skin = self.config.images.skin[self.skin_id]
    
    def previous(self):
        self.skin_id -= 1
        if self.skin_id == -1:
            self.skin_id = 2
            self.skin = self.config.images.skin[self.skin_id]
        else:
            self.skin = self.config.images.skin[self.skin_id]

    def draw(self):
        if self.player_id == "0":
            posSkin = (375, 215)
            self.config.screen.blit(self.skin, posSkin)

        elif self.player_id == "1":
            posSkin = (600, 215)
            self.config.screen.blit(self.skin, posSkin)

        elif self.player_id == "2":
            posSkin = (375, 375)
            self.config.screen.blit(self.skin, posSkin)
            
        elif self.player_id == "3":
            posSkin = (600, 375)
            self.config.screen.blit(self.skin, posSkin)