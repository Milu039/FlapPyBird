import pygame
from ..utils import GameConfig, Mode
from .entity import Entity

class Button(Entity):
    def __init__(self, config: GameConfig, mode: Mode) -> None:
        super().__init__(config)
        self.mode = mode
        self.resume_button = self.config.images.buttons["resume"]
        self.restart_button = self.config.images.buttons["restart"]
        self.quit_button = self.config.images.buttons["quit"]
        self.create_button = self.config.images.buttons["create"]
        self.join_button = self.config.images.buttons["join"]
        self.ready_button = self.config.images.buttons["ready"]

    def set_mode(self, mode) -> None:
        self.mode = mode

    def draw(self) -> None:
        # Draw the buttons based on the game mode
        if self.mode == "Pause":
            self.resume_pos = ((self.config.window.width - self.resume_button.get_width()) // 2, (self.config.window.height - self.restart_button.get_height()) // 3)
            self.restart_pos = ((self.config.window.width - self.restart_button.get_width()) // 2, (self.config.window.height - self.restart_button.get_height()) * 1.5 // 3)
            self.quit_pos = ((self.config.window.width - self.quit_button.get_width()) // 2, (self.config.window.height - self.restart_button.get_height()) * 2 // 3)

            self.draw_button(self.resume_button, self.resume_pos)
            self.draw_button(self.restart_button, self.restart_pos)
            self.draw_button(self.quit_button, self.quit_pos)

            self.resume_rect = self.create_button_rect(self.resume_pos, self.resume_button)
            self.restart_rect = self.create_button_rect(self.restart_pos, self.restart_button)
            self.quit_rect = self.create_button_rect(self.quit_pos, self.quit_button)

        if self.mode == "Solo GameOver" or self.mode == "Leaderboard":
            self.restart_pos = (325, self.config.window.height // 2 + 100)
            self.quit_pos = (540, self.config.window.height // 2 + 100)

            self.draw_button(self.restart_button, self.restart_pos)
            self.draw_button(self.quit_button, self.quit_pos)

            self.restart_rect = self.create_button_rect(self.restart_pos, self.restart_button)
            self.quit_rect = self.create_button_rect(self.quit_pos, self.quit_button)

        if self.mode == "Game Room":
            self.create_pos = (325, self.config.window.height // 2 + 150)
            self.join_pos = (540, self.config.window.height // 2 + 150)

            self.draw_button(self.create_button, self.create_pos)
            self.draw_button(self.join_button, self.join_pos)

            self.create_rect = self.create_button_rect(self.create_pos, self.create_button)
            self.join_rect = self.create_button_rect(self.join_pos, self.join_button)
        
        if self.mode == "Create Room":
            self.create_pos = ((self.config.window.width - self.create_button.get_width()) // 2, self.config.window.height // 2 + 150)
            self.draw_button(self.create_button, self.create_pos)
            self.create_rect = self.create_button_rect(self.create_pos, self.create_button)
        
        if self.mode == "Room Lobby":
            self.ready_pos = ((self.config.window.width - self.ready_button.get_width()) // 2, self.config.window.height // 2 + 150)
            self.draw_button(self.ready_button, self.ready_pos)
            self.ready_rect = self.create_button_rect(self.ready_pos, self.ready_button)

    def draw_button(self,image,pos) -> None:
        self.config.screen.blit(image, pos)
    
    def create_button_rect(self, pos, image) -> pygame.Rect:
        return pygame.Rect(pos[0], pos[1], image.get_width(), image.get_height())