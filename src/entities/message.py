import pygame
import random as Random
from ..utils import GameConfig, Mode
from .entity import Entity


class Message(Entity):
    def __init__(self, config: GameConfig, mode: Mode) -> None:
        super().__init__(config)
        self.mode = mode
        self.random_number = Random.randint(100000, 999999)
        self.ready_message = config.images.message["ready"]
        self.game_room_message = config.images.message["game room"]
        self.create_room_message = config.images.message["create"]
        self.game_over_message = config.images.message["gameover"]
    
    def set_mode(self, mode) -> None:
        self.mode = mode

    def draw_message(self,image,pos) -> None:
        self.config.screen.blit(image, pos)

    def draw(self):
        if self.mode == "Solo":
            self.ready_pos = ((self.config.window.width - self.ready_message.get_width()) // 2, int(self.config.window.height * 0.12))
            self.draw_message(self.ready_message, self.ready_pos)
        if self.mode == "Solo GameOver":
            self.game_over_pos = ((self.config.window.width - self.game_over_message.get_width()) // 2, int(self.config.window.height * 0.1))
            self.draw_message(self.game_over_message, self.game_over_pos)
        if self.mode == "Game Room":
            self.game_room_pos = ((self.config.window.width - self.game_room_message.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(self.game_room_message, self.game_room_pos)
        if self.mode == "Create Room":
            FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 24)
            WHITE = (255, 255, 255)
            BLACK = (0,0,0)

            self.create_pos = ((self.config.window.width - self.create_room_message.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(self.create_room_message, self.create_pos)

            # Room Number Label
            self.room_number_sur = FONT.render("Room Number", True, BLACK)
            self.room_number_rect = self.room_number_sur.get_rect(
                center=(
                    int(self.config.window.width // 2),  
                    int(self.config.window.height * 0.275)
                    )
                )
            self.draw_message(self.room_number_sur, self.room_number_rect)

            # Room Number Text Field
            room_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 260, 300, 40)
            pygame.draw.rect(self.config.screen, WHITE, room_input_rect)
            pygame.draw.rect(self.config.screen, BLACK, room_input_rect, 2)
            room_input_surface = FONT.render(str(self.random_number), True, BLACK)
            self.config.screen.blit(room_input_surface, (room_input_rect.x + 10, room_input_rect.y + 8))

            # Password Label
            password_label = FONT.render("Password", True, BLACK)
            password_rect = password_label.get_rect(center=(int(self.config.window.width // 2),  int(self.config.window.height * 0.46)))
            self.draw_message(password_label, password_rect)

            # Password Text Field
            password_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 400, 300, 40)
            pygame.draw.rect(self.config.screen, WHITE, password_input_rect)
            pygame.draw.rect(self.config.screen, BLACK, password_input_rect, 2)

            password_input_surface = FONT.render("***", True, BLACK)
            self.config.screen.blit(password_input_surface, (password_input_rect.x + 10, password_input_rect.y + 8))

        if self.mode == "Leaderboard":
            pass

