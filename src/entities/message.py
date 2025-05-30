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

        # solo
        self.ready_message = config.images.message["ready"]
        self.game_over_message = config.images.message["gameover"]

        # multi
        # game room
        self.game_room_message = config.images.message["game room"]
        self.txtPassword = ""
        self.show_password_prompt = False
        self.password_error = False
        self.password_active = False
        self.password_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 325, 300, 40)

        # create room
        self.random_number = Random.randint(100000, 999999)
        self.create_room_message = config.images.message["create"]

        # room lobby
        self.room_num = self.random_number
        self.player_id = None
        self.host_icon = config.images.icon["host"]
        self.kick_icon = config.images.icon["kick"]
        self.ready_icon = config.images.icon["ready"]
    
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

        elif self.mode == "Solo GameOver":
            self.game_over_pos = ((self.config.window.width - self.game_over_message.get_width()) // 2, int(self.config.window.height * 0.1))
            self.draw_message(self.game_over_message, self.game_over_pos)

        elif self.mode == "Game Room":
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
                    self.roomNum = room.split(':')[1].split(',')[0].strip()
                    # Change to text format
                    txtRoomNo = self.FONT.render(roomNo, True, self.BLACK)
                    txtRoomNum = self.FONT.render(self.roomNum, True, self.BLACK)
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

            if self.show_password_prompt:
                messageBox = self.config.images.container["message box"]
                posMessageBox = (int((self.config.window.width - messageBox.get_width()) // 2), int((self.config.window.height - messageBox.get_height()) // 2))
                self.draw_message(messageBox, posMessageBox)

                # Draw label
                lblPassword = self.FONT.render("Room Password:", True, self.BLACK)
                posPassword = (self.config.window.width // 2 - lblPassword.get_width() // 2, 275)
                self.draw_message(lblPassword, posPassword)

                # Draw input field (red if error)
                color = (255, 0, 0) if self.password_error else self.BLACK
                pygame.draw.rect(self.config.screen, self.WHITE, self.password_input_rect)
                pygame.draw.rect(self.config.screen, color, self.password_input_rect, 2)

                # Draw text inside input
                masked = "*" * len(self.txtPassword)
                password_surface = self.FONT.render(masked, True, self.BLACK)
                self.config.screen.blit(password_surface, (self.password_input_rect.x + 10, self.password_input_rect.y + 8))

                # Draw error message
                if self.password_error:
                    error_msg = self.FONT.render("Incorrect password", True, (255, 0, 0))
                    error_pos = (self.config.window.width // 2 - error_msg.get_width() // 2, self.password_input_rect.y + 60)
                    self.config.screen.blit(error_msg, error_pos)

        elif self.mode == "Create Room":
            self.create_pos = ((self.config.window.width - self.create_room_message.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(self.create_room_message, self.create_pos)

            # Room Number Label
            lblRoomNumber = self.FONT.render("Room Number", True, self.BLACK)
            posRoomNumber = (int((self.config.window.width - lblRoomNumber.get_width()) // 2), self.config.window.height // 2 - 125 )
            self.draw_message(lblRoomNumber, posRoomNumber)

            # Room Number Text Field
            self.room_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 300, 300, 40)
            pygame.draw.rect(self.config.screen, self.WHITE, self.room_input_rect)
            pygame.draw.rect(self.config.screen, self.BLACK, self.room_input_rect, 2)
            self.room_input_surface = self.FONT.render(str(self.random_number), True, self.BLACK)
            self.config.screen.blit(self.room_input_surface, (self.room_input_rect.x + 10, self.room_input_rect.y + 8))

            # Password Label
            lblPassword = self.FONT.render("Password", True, self.BLACK)
            posPassword = (int((self.config.window.width - lblPassword.get_width()) // 2),  self.config.window.height // 2 - 20)
            self.draw_message(lblPassword, posPassword)

            # Password Text Field
            self.password_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 400, 300, 40)
            pygame.draw.rect(self.config.screen, self.WHITE, self.password_input_rect)
            pygame.draw.rect(self.config.screen, self.BLACK, self.password_input_rect, 2)

            masked = "*" * len(self.txtPassword)
            password_input_surface = self.FONT.render(masked, True, self.BLACK)
            self.config.screen.blit(password_input_surface, (self.password_input_rect.x + 10, self.password_input_rect.y + 8))
        
        elif self.mode == "Room Lobby: host" or "Room Lobby: member":
            room_title = f"Room {self.room_num}"
            font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 20)
            # Colors
            brown = (66, 36, 0)
            orange = (234, 92, 0)
            # Sizes and positions
            x, y = (self.config.window.width - self.create_room_message.get_width()) // 2, int(self.config.window.height * 0.05)
            width, height = 306, 63  # Outer border size
            # Draw outer brown border
            pygame.draw.rect(self.config.screen, brown, (x, y, width, height))
            # Draw white inner border
            padding = 5
            pygame.draw.rect(self.config.screen, self.WHITE, (x + padding, y + padding, width - 2 * padding, height - 2 * padding))
            # Draw orange inner box
            inner_padding = 5
            pygame.draw.rect(self.config.screen, orange, (x + padding + inner_padding, y + padding + inner_padding,
                                            width - 2 * (padding + inner_padding),
                                            height - 2 * (padding + inner_padding)))
            # Draw text centered
            text_surface = font.render(room_title, True, self.WHITE)
            text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
            self.draw_message(text_surface, text_rect)

            if self.player_id == "0":
                posHost = (295,278)
                self.draw_message(self.host_icon, posHost)

                surPlayer = self.FONT.render("Player 1", True, self.BLACK)
                self.rectPlayer = surPlayer.get_rect(center=(400, 295))
                self.draw_message(surPlayer, self.rectPlayer)

            elif self.player_id == "1":
                posReady = (515, 285)
                self.draw_message(self.ready_icon, posReady)

                surPlayer = self.FONT.render("Player 2", True, self.BLACK)
                self.rectPlayer = surPlayer.get_rect(center=(625, 295))
                self.draw_message(surPlayer, self.rectPlayer)
            
            elif self.player_id == "2":
                posReady = (295, 445)
                self.draw_message(self.ready_icon, posReady)

                surPlayer = self.FONT.render("Player 3", True, self.BLACK)
                self.rectPlayer = surPlayer.get_rect(center=(400, 455))
                self.draw_message(surPlayer, self.rectPlayer)
            
            elif self.player_id == "3":
                posReady = (515, 445)
                self.draw_message(self.ready_icon, posReady)

                surPlayer = self.FONT.render("Player 4", True, self.BLACK)
                self.rectPlayer = surPlayer.get_rect(center=(625, 455))
                self.draw_message(surPlayer, self.rectPlayer)

        elif self.mode == "Leaderboard":
            pass
        elif self.mode == "skill_ability" or self.mode == "Skill Ability":
            # Draw the skill ability image instead of generating text
            skill_ability_img = self.config.images.message["skill_ability"]
            skill_ability_pos = ((self.config.window.width - skill_ability_img.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(skill_ability_img, skill_ability_pos)

