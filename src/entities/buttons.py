import pygame
from ..utils import GameConfig, GameMode
from .entity import Entity
from .player import PlayerMode

class Button(Entity):
    def __init__(self, config: GameConfig, game_mode : GameMode) -> None:
        super().__init__(config)
        self.game_mode = game_mode

    def draw(self) -> None:
        #print(self.game_mode)
        if self.game_mode == "solo":
            restart_button = self.config.images.buttons["restart"]
            quit_button = self.config.images.buttons["quit"]

            restart_pos = (325, self.config.window.height // 2 + 100)
            quit_pos = (540, self.config.window.height // 2 + 100)

            self.draw_button(restart_button, restart_pos)
            self.draw_button(quit_button, quit_pos)

            self.restart_rect = self.create_button_rect(restart_pos, restart_button)
            self.quit_rect = self.create_button_rect(quit_pos, quit_button)

        elif self.game_mode == "multi":
            create_button = self.config.images.buttons["create"]
            join_button = self.config.images.buttons["join"]

            create_pos = (325, self.config.window.height // 2 + 90)
            join_pos = (540, self.config.window.height // 2 + 90)

            self.draw_button(create_button, create_pos)
            self.draw_button(join_button, join_pos)

            self.create_rect = self.create_button_rect(create_pos, create_button)
            self.join_rect = self.create_button_rect(join_pos, join_button)

    def draw_button(self,image,pos) -> None:
        self.config.screen.blit(image, pos)
    
    def create_button_rect(self, pos, image) -> pygame.Rect:
        return pygame.Rect(pos[0], pos[1], image.get_width(), image.get_height())