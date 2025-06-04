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
        self.roomCapacity = 0
        self.player_id = None
        self.txtPlayerName = ""
        self.show_name_prompt = False
        self.name_error = False
        self.change_name_active = False
        self.name_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 325, 300, 40)
        self.host_icon = config.images.icon["host"]
        self.isHost = False
        self.ready_icon = config.images.icon["ready"]
        self.isReady = False
    
    def set_mode(self, mode) -> None:
        self.mode = mode

    def set_rooms(self, room_list):
        self.rooms = room_list

    def draw_message(self, image, pos) -> None:
        self.config.screen.blit(image, pos)

    def draw_name(self, players):
        positions = [
            (295, 278),  # Player 0 (Top Left)
            (515, 285),  # Player 1 (Top Right)
            (295, 445),  # Player 2 (Bottom Left)
            (515, 445),  # Player 3 (Bottom Right)
        ]
        name_centers = [
            (400, 295),
            (625, 295),
            (400, 455),
            (625, 455),
        ]

        for i, player in enumerate(players):
            if player is None:
                continue

            player_id = player.get("player_id", i)
            name = player.get("name", f"Player {i+1}")
            is_ready = player.get("ready")
            is_host = player.get("host")

            # Draw host or ready icon
            if is_host:
                self.draw_message(self.host_icon, positions[i])
            elif is_ready:
                self.draw_message(self.ready_icon, positions[i])

            # Draw player name
            name_surface = self.FONT.render(name, True, self.BLACK)
            name_rect = name_surface.get_rect(center=name_centers[i])
            self.draw_message(name_surface, name_rect)

            # Only set rectPlayer if it's the local player
            if player_id == int(self.player_id):
                self.rectPlayer = name_rect

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
                    roomNo = room.split(':')[0].strip()
                    self.roomNum = room.split(':')[1].strip()
                    self.roomCapacity = int(room.split(':')[3].strip())
                    txtRoomNo = self.FONT.render(roomNo, True, self.BLACK)
                    txtRoomNum = self.FONT.render(self.roomNum, True, self.BLACK)

                    if self.roomCapacity == 1:
                        txtPerson = self.FONT.render("1/4", True, self.BLACK)
                    elif self.roomCapacity == 2:
                        txtPerson = self.FONT.render("2/4", True, self.BLACK)
                    elif self.roomCapacity == 3:
                        txtPerson = self.FONT.render("3/4", True, self.BLACK)

                    row_rect = pygame.Rect(200, posRoom-10, 600, 40)
                    self.rectRoom.append(row_rect)

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

                lblPassword = self.FONT.render("Room Password:", True, self.BLACK)
                posPassword = (self.config.window.width // 2 - lblPassword.get_width() // 2, 275)
                self.draw_message(lblPassword, posPassword)

                color = (255, 0, 0) if self.password_error else self.BLACK
                pygame.draw.rect(self.config.screen, self.WHITE, self.password_input_rect)
                pygame.draw.rect(self.config.screen, color, self.password_input_rect, 2)

                masked = "*" * len(self.txtPassword)
                password_surface = self.FONT.render(masked, True, self.BLACK)
                self.config.screen.blit(password_surface, (self.password_input_rect.x + 10, self.password_input_rect.y + 8))

                if self.password_error:
                    error_msg = self.FONT.render("Incorrect password", True, (255, 0, 0))
                    error_pos = (self.config.window.width // 2 - error_msg.get_width() // 2, self.password_input_rect.y + 60)
                    self.config.screen.blit(error_msg, error_pos)

        elif self.mode == "Create Room":
            self.create_pos = ((self.config.window.width - self.create_room_message.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(self.create_room_message, self.create_pos)

            lblRoomNumber = self.FONT.render("Room Number", True, self.BLACK)
            posRoomNumber = (int((self.config.window.width - lblRoomNumber.get_width()) // 2), self.config.window.height // 2 - 125 )
            self.draw_message(lblRoomNumber, posRoomNumber)

            self.room_input_rect = pygame.Rect(self.config.window.width // 2 - 60, 300, 300, 40)
            self.room_input_surface = self.FONT.render(str(self.random_number), True, self.BLACK)
            self.config.screen.blit(self.room_input_surface, (self.room_input_rect.x + 10, self.room_input_rect.y + 8))

            lblPassword = self.FONT.render("Password", True, self.BLACK)
            posPassword = (int((self.config.window.width - lblPassword.get_width()) // 2),  self.config.window.height // 2 - 20)
            self.draw_message(lblPassword, posPassword)

            self.password_input_rect = pygame.Rect(self.config.window.width // 2 - 150, 400, 300, 40)
            pygame.draw.rect(self.config.screen, self.WHITE, self.password_input_rect)
            pygame.draw.rect(self.config.screen, self.BLACK, self.password_input_rect, 2)

            masked = "*" * len(self.txtPassword)
            password_input_surface = self.FONT.render(masked, True, self.BLACK)
            self.config.screen.blit(password_input_surface, (self.password_input_rect.x + 10, self.password_input_rect.y + 8))

        elif self.mode == "Room Lobby: host" or "Room Lobby: member":
            room_title = f"Room {self.room_num}"
            font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 20)
            brown = (66, 36, 0)
            orange = (234, 92, 0)
            x, y = (self.config.window.width - self.create_room_message.get_width()) // 2, int(self.config.window.height * 0.05)
            width, height = 306, 63
            pygame.draw.rect(self.config.screen, brown, (x, y, width, height))
            padding = 5
            pygame.draw.rect(self.config.screen, self.WHITE, (x + padding, y + padding, width - 2 * padding, height - 2 * padding))
            inner_padding = 5
            pygame.draw.rect(self.config.screen, orange, (x + padding + inner_padding, y + padding + inner_padding,
                                            width - 2 * (padding + inner_padding),
                                            height - 2 * (padding + inner_padding)))
            text_surface = font.render(room_title, True, self.WHITE)
            text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
            self.draw_message(text_surface, text_rect)

            if self.show_name_prompt:
                messageBox = self.config.images.container["message box"]
                posMessageBox = (int((self.config.window.width - messageBox.get_width()) // 2), int((self.config.window.height - messageBox.get_height()) // 2))
                self.draw_message(messageBox, posMessageBox)

                lblName = self.FONT.render("Name:", True, self.BLACK)
                posName = (self.config.window.width // 2 - lblName.get_width() // 2, 275)
                self.draw_message(lblName, posName)

                color = (255, 0, 0) if self.password_error else self.BLACK
                pygame.draw.rect(self.config.screen, self.WHITE, self.name_input_rect)
                pygame.draw.rect(self.config.screen, color, self.name_input_rect, 2)

                name_surface = self.FONT.render(self.txtPlayerName, True, self.BLACK)
                self.config.screen.blit(name_surface, (self.name_input_rect.x + 10, self.name_input_rect.y + 8))

                if self.name_error:
                    error_msg = self.FONT.render("No Empty Name", True, (255, 0, 0))
                    error_pos = (self.config.window.width // 2 - error_msg.get_width() // 2, self.name_input_rect.y + 60)
                    self.config.screen.blit(error_msg, error_pos)

        elif self.mode == "Leaderboard":
            pass

        elif self.mode == "skill_ability" or self.mode == "Skill Ability":
            # Draw the skill ability image instead of generating text
            skill_ability_img = self.config.images.message["skill_ability"]
            skill_ability_pos = ((self.config.window.width - skill_ability_img.get_width()) // 2, int(self.config.window.height * 0.05))
            self.draw_message(skill_ability_img, skill_ability_pos)

