import pygame
from ..utils import GameConfig, Mode
from .entity import Entity

class Button(Entity):
    def __init__(self, config: GameConfig, mode: Mode) -> None:
        super().__init__(config)
        self.mode = mode
        self.show_password_prompt = False
        self.show_name_prompt = False
        self.player_id = None
        self.btnResume = config.images.buttons["resume"]
        self.btnRestart = config.images.buttons["restart"]
        self.btnQuit = config.images.buttons["quit"]
        self.btnCreate = config.images.buttons["create"]
        self.btnJoin = config.images.buttons["join"]
        self.btnEnter = config.images.buttons["enter"]
        self.btnCancel = config.images.buttons["cancel"]

        # host start button
        self.ready_count = 0
        self.btnStart_1_4 = config.images.buttons["start (1/4)"]
        self.btnStart_1_4.set_alpha(191)
        self.btnStart_2_4 = config.images.buttons["start (2/4)"]
        self.btnStart_2_4.set_alpha(191)
        self.btnStart_3_4 = config.images.buttons["start (3/4)"]
        self.btnStart_3_4.set_alpha(191)
        self.btnStart = self.config.images.buttons["start"]

        # member ready button
        self.btnReady = config.images.buttons["ready"]
        self.isReady = False

        # change skin button
        self.btnNextSkin = config.images.buttons["next"]
        self.btnPreSkin = config.images.buttons["previous"]

        # kick button
        self.roomCapacity = 0
        self.btnKickPlayer = config.images.icon["kick"]
        self.rectKicks = []
        self.kick_targets = []

    def set_mode(self, mode) -> None:
        self.mode = mode

    def update_kick_buttons(self, lobby_state):
        kick_positions_map = {
            2: [(515, 185)],
            3: [(515, 185), (295, 345)],
            4: [(515, 185), (295, 345), (515, 345)],
        }

        self.rectKicks = []
        self.kick_targets = []

        # Get the correct number of positions for other players (excluding self)
        other_players = [p for p in lobby_state if p["player_id"] != int(self.player_id)]
        positions = kick_positions_map.get(len(lobby_state), [])

        for target, pos in zip(other_players, positions):
            self.draw_button(self.btnKickPlayer, pos)
            rect = self.btnrectCreate(pos, self.btnKickPlayer)
            self.rectKicks.append(rect)
            self.kick_targets.append(target["player_id"])


    def draw_enter_cancel_button(self):
        self.posEnter = (self.config.window.width // 2 - 150, 425)
        self.draw_button(self.btnEnter, self.posEnter)
        self.rectEnter = self.btnrectCreate(self.posEnter, self.btnEnter)

        self.posCancel = (self.config.window.width // 2 + 7, 425)
        self.draw_button(self.btnCancel, self.posCancel)
        self.rectCancel = self.btnrectCreate(self.posCancel, self.btnCancel)

    def draw(self) -> None:
        # Draw the buttons based on the game mode
        if self.mode == "Pause":
            self.posResume = ((self.config.window.width - self.btnResume.get_width()) // 2, (self.config.window.height - self.btnRestart.get_height()) // 3)
            self.posRestart = ((self.config.window.width - self.btnRestart.get_width()) // 2, (self.config.window.height - self.btnRestart.get_height()) * 1.5 // 3)
            self.posQuit = ((self.config.window.width - self.btnQuit.get_width()) // 2, (self.config.window.height - self.btnRestart.get_height()) * 2 // 3)

            self.draw_button(self.btnResume, self.posResume)
            self.draw_button(self.btnRestart, self.posRestart)
            self.draw_button(self.btnQuit, self.posQuit)

            self.rectResume = self.btnrectCreate(self.posResume, self.btnResume)
            self.rectRestart = self.btnrectCreate(self.posRestart, self.btnRestart)
            self.rectQuit = self.btnrectCreate(self.posQuit, self.btnQuit)

        if self.mode == "Solo GameOver" or self.mode == "Leaderboard":
            self.posRestart = (325, self.config.window.height // 2 + 100)
            self.posQuit = (540, self.config.window.height // 2 + 100)

            self.draw_button(self.btnRestart, self.posRestart)
            self.draw_button(self.btnQuit, self.posQuit)

            self.rectRestart = self.btnrectCreate(self.posRestart, self.btnRestart)
            self.rectQuit = self.btnrectCreate(self.posQuit, self.btnQuit)

        if self.mode == "Game Room":
            self.posCreate = (300, self.config.window.height // 2 + 275)
            self.posJoin = (575, self.config.window.height // 2 + 275)

            self.draw_button(self.btnCreate, self.posCreate)
            self.draw_button(self.btnJoin, self.posJoin)

            self.rectCreate = self.btnrectCreate(self.posCreate, self.btnCreate)
            self.rectJoin = self.btnrectCreate(self.posJoin, self.btnJoin)

            if self.show_password_prompt:
                self.draw_enter_cancel_button()

        if self.mode == "Create Room":
            self.posCreate = ((self.config.window.width - self.btnCreate.get_width()) // 2, self.config.window.height // 2 + 100)
            self.draw_button(self.btnCreate, self.posCreate)
            self.rectCreate = self.btnrectCreate(self.posCreate, self.btnCreate)

        if self.mode == "Room Lobby: host": # kick icon is ok but kick function not ok
            self.posNext = (450, 215)
            self.posPrevious = (325, 215)

            self.draw_button(self.btnNextSkin, self.posNext)
            self.draw_button(self.btnPreSkin, self.posPrevious)
            self.rectPreSkin = self.btnrectCreate(self.posPrevious, self.btnPreSkin)
            self.rectNextSkin = self.btnrectCreate(self.posNext, self.btnNextSkin)

            start_buttons = {
                0: self.btnStart_1_4,
                1: self.btnStart_2_4,
                2: self.btnStart_3_4
            }
            
            if self.ready_count in start_buttons:
                button = start_buttons[self.ready_count]
                button.set_alpha(191)
                self.posStart = ((self.config.window.width - button.get_width()) // 2, self.config.window.height // 2 + 175)
                self.draw_button(button, self.posStart)
                
            elif self.ready_count == 3:
                self.posStart = ((self.config.window.width - self.btnStart.get_width()) // 2, self.config.window.height // 2 + 175)
                self.draw_button(self.btnStart, self.posStart)
                self.rectStart = self.btnrectCreate(self.posStart, self.btnStart)
            '''
            if self.ready.count == 1:
                self.posStart = ((self.config.window.width - self.btnStart.get_width()) // 2, self.config.window.height // 2 + 175)
                self.draw_button(self.btnStart, self.posStart)
                self.rectStart = self.btnrectCreate(self.posStart, self.btnStart)'''

            if self.show_name_prompt:
                self.draw_enter_cancel_button()

        if self.mode == "Room Lobby: member":
            if self.player_id == "1":
                self.posNext = (675, 215)
                self.posPrevious = (550, 215)

            elif self.player_id == "2":
                self.posNext = (450, 375)
                self.posPrevious = (325, 375)

            elif self.player_id == "3":
                self.posNext = (675, 375)
                self.posPrevious = (550, 375)
            
            if self.isReady:
                self.posCancel = ((self.config.window.width - self.btnReady.get_width()) // 2, self.config.window.height // 2 + 175)
                self.draw_button(self.btnCancel, self.posCancel)
                self.rectCancel = self.btnrectCreate(self.posCancel, self.btnReady)
            else:
                self.draw_button(self.btnNextSkin, self.posNext)
                self.draw_button(self.btnPreSkin, self.posPrevious)
                self.rectNextSkin = self.btnrectCreate(self.posNext, self.btnNextSkin)
                self.rectPreSkin = self.btnrectCreate(self.posPrevious, self.btnPreSkin)
                self.posReady = ((self.config.window.width - self.btnReady.get_width()) // 2, self.config.window.height // 2 + 175)
                self.draw_button(self.btnReady, self.posReady)
                self.rectReady = self.btnrectCreate(self.posReady, self.btnReady)

            if self.show_name_prompt:
                self.draw_enter_cancel_button()

    def draw_button(self,image,pos) -> None:
        self.config.screen.blit(image, pos)

    def btnrectCreate(self, pos, image) -> pygame.Rect:
        return pygame.Rect(pos[0], pos[1], image.get_width(), image.get_height())
