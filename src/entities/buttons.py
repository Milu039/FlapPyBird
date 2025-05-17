import pygame
from ..utils import GameConfig
from .entity import Entity

class Button(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(config)

    def draw(self) -> None:
        restart_button = self.config.images.buttons["restart"]
        quit_button = self.config.images.buttons["quit"]

        restart_pos = (325, self.config.window.height // 2 + 100)
        quit_pos = (540, self.config.window.height // 2 + 100)

        self.config.screen.blit(restart_button, restart_pos)
        self.config.screen.blit(quit_button, quit_pos)

        # Store rectangles for click detection
        self.restart_rect = pygame.Rect(
            restart_pos[0], restart_pos[1],
            restart_button.get_width(), restart_button.get_height()
        )
        self.quit_rect = pygame.Rect(
            quit_pos[0], quit_pos[1],
            quit_button.get_width(), quit_button.get_height()
        )
