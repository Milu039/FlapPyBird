import pygame
import random as Random
from ..utils import GameConfig, Mode
from .entity import Entity


class Message(Entity):
    def __init__(self, config: GameConfig, mode: Mode) -> None:
        super().__init__(config)
        self.mode = mode
        self.FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 16)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0,0,0)
        self.mode = mode
        self.random_number = Random.randint(100000, 999999)
        self.ready_message = config.images.message["ready"]
        self.game_room_message = config.images.message["game room"]
        self.create_room_message = config.images.message["create"]
        self.txtPassword = ""
        self.password_active = False
        self.game_over_message = config.images.message["gameover"]
    
    def set_mode(self, mode) -> None:
        self.mode = mode

    def set_rooms(self, room_list):
        self.rooms = room_list

    def draw_message(self, image, pos) -> None:
        self.config.screen.blit(image, pos)

    def draw(self, selected_room=None, mouse_pos=None):
        if self.mode == "Solo":
            self.ready_pos = ((self.config.window.width - self.ready_message.get_width()) // 2, int(self.config.window.height * 0.12))
            self.draw_message(self.ready_message, self.ready_pos)
        if self.mode == "Solo GameOver":
            self.game_over_pos = ((self.config.window.width - self.game_over_message.get_width()) // 2, int(self.config.window.height * 0.1))
            self.draw_message(self.game_over_message, self.game_over_pos)
        if self.mode == "Game Room":
            self.game_room_pos = ((self.config.window.width - self.game_room_message.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(self.game_room_message, self.game_room_pos)
            
            lblNo = self.FONT.render("No", True, self.BLACK)
            posNo = (225,  175)
            self.draw_message(lblNo, posNo)

            lblRoomNumber = self.FONT.render("Room Number", True, self.BLACK)
            posRoomNumber = (int((self.config.window.width - lblRoomNumber.get_width()) // 2),  175)
            self.draw_message(lblRoomNumber, posRoomNumber)

            lblPerson = self.FONT.render("Person", True, self.BLACK)
            posPerson = (685,  175)
            self.draw_message(lblPerson, posPerson)

            self.rectRoom = []
            posRoom = 225
            if self.rooms:
                for index, room in enumerate(self.rooms):
                    # Get room no and room number from room list
                    roomNo = room.split(':')[0].strip()
                    roomNum = room.split(':')[1].split(',')[0].strip()
                    # Change to text format
                    txtRoomNo = self.FONT.render(roomNo, True, self.BLACK)
                    txtRoomNum = self.FONT.render(roomNum, True, self.BLACK)
                    txtPerson = self.FONT.render("1/4", True, self.BLACK)
                    # Draw rect for text
                    row_rect = pygame.Rect(200, posRoom-10, 600, 40)
                    self.rectRoom.append(row_rect)
                    
                    # Draw highlight if hovered or selected
                    is_hovered = mouse_pos and row_rect.collidepoint(mouse_pos)
                    is_selected = selected_room == index

                    if is_selected or is_hovered:
                        pygame.draw.rect(self.config.screen, (139, 69, 19), row_rect)

                    self.config.screen.blit(txtRoomNo, (225, posRoom))
                    self.config.screen.blit(txtRoomNum, (int((self.config.window.width - txtRoomNum.get_width()) // 2), posRoom))
                    self.config.screen.blit(txtPerson, (715, posRoom))
                    posRoom += 50

        if self.mode == "Create Room":
            self.create_pos = ((self.config.window.width - self.create_room_message.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(self.create_room_message, self.create_pos)

            # Room Number Label
            lblRoomNumber = self.FONT.render("Room Number", True, self.BLACK)
            posRoomNumber = (int((self.config.window.width - lblRoomNumber.get_width()) // 2),  int(self.config.window.height * 0.275))
            self.draw_message(lblRoomNumber, posRoomNumber)

            # Room Number Text Field
            self.room_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 260, 300, 40)
            pygame.draw.rect(self.config.screen, self.WHITE, self.room_input_rect)
            pygame.draw.rect(self.config.screen, self.BLACK, self.room_input_rect, 2)
            self.room_input_surface = self.FONT.render(str(self.random_number), True, self.BLACK)
            self.config.screen.blit(self.room_input_surface, (self.room_input_rect.x + 10, self.room_input_rect.y + 8))

            # Password Label
            lblPassword = self.FONT.render("Password", True, self.BLACK)
            posPassword = (int((self.config.window.width - lblPassword.get_width()) // 2),  int(self.config.window.height * 0.46))
            self.draw_message(lblPassword, posPassword)

            # Password Text Field
            self.password_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 400, 300, 40)
            pygame.draw.rect(self.config.screen, self.WHITE, self.password_input_rect)
            pygame.draw.rect(self.config.screen, self.BLACK, self.password_input_rect, 2)

            masked = "*" * len(self.txtPassword)
            password_input_surface = self.FONT.render(masked, True, self.BLACK)
            self.config.screen.blit(password_input_surface, (self.password_input_rect.x + 10, self.password_input_rect.y + 8))

        if self.mode == "Leaderboard":
            pass

        if self.mode == "skill_ability":
            self.game_room_pos = ((self.config.window.width - self.game_room_message.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(self.game_room_message, self.game_room_pos)

