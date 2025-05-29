import pygame
from ..utils import GameConfig, Mode
from .entity import Entity

class Button(Entity):
    def __init__(self, config: GameConfig, mode: Mode) -> None:
        super().__init__(config)
        self.mode = mode
        self.show_password_prompt = False
        self.btnResume = self.config.images.buttons["resume"]
        self.btnRestart = self.config.images.buttons["restart"]
        self.btnQuit = self.config.images.buttons["quit"]
        self.btnCreate = self.config.images.buttons["create"]
        self.btnJoin = self.config.images.buttons["join"]
        self.btnEnter = self.config.images.buttons["enter"]
        self.btnCancel = self.config.images.buttons["cancel"]

        self.btnStart_1_2 = self.config.images.buttons["start (1/2)"]
        self.btnStart_1_2.set_alpha(191)
        self.btnStart_1_3 = self.config.images.buttons["start (1/3)"]
        self.btnStart_1_3.set_alpha(191)
        self.btnStart_2_3 = self.config.images.buttons["start (2/3)"]
        self.btnStart_2_3.set_alpha(191)
        self.btnStart_1_4 = self.config.images.buttons["start (1/4)"]
        self.btnStart_1_4.set_alpha(191)
        self.btnStart_2_4 = self.config.images.buttons["start (2/4)"]
        self.btnStart_2_4.set_alpha(191)
        self.btnStart_3_4 = self.config.images.buttons["start (3/4)"]
        self.btnStart_3_4.set_alpha(191)

        self.btnStart = self.config.images.buttons["start"]
        self.btnReady = self.config.images.buttons["ready"]

    def set_mode(self, mode) -> None:
        self.mode = mode

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
                self.posEnter = (self.config.window.width // 2 - 150, 425)
                self.draw_button(self.btnEnter, self.posEnter)
                self.rectEnter = self.btnrectCreate(self.posEnter, self.btnEnter)

                self.posCancel = (self.config.window.width // 2 + 7, 425)
                self.draw_button(self.btnCancel, self.posCancel)
                self.rectCancel = self.btnrectCreate(self.posCancel, self.btnCancel)
        
        if self.mode == "Create Room":
            self.posCreate = ((self.config.window.width - self.btnCreate.get_width()) // 2, self.config.window.height // 2 + 150)
            self.draw_button(self.btnCreate, self.posCreate)
            self.rectCreate = self.btnrectCreate(self.posCreate, self.btnCreate)
        
        if self.mode == "Room Lobby: host":
            self.btnStart.set_alpha(191)
            self.posStart = ((self.config.window.width - self.btnStart.get_width()) // 2, self.config.window.height // 2 + 150)
            self.draw_button(self.btnStart, self.posStart)
            self.rectStart = self.btnrectCreate(self.posStart, self.btnStart)

        if self.mode == "Room Lobby: member":
            self.posReady = ((self.config.window.width - self.btnReady.get_width()) // 2, self.config.window.height // 2 + 150)
            self.draw_button(self.btnReady, self.posReady)
            self.rectReady = self.btnrectCreate(self.posReady, self.btnReady)

    def draw_button(self,image,pos) -> None:
        self.config.screen.blit(image, pos)
    
    def btnrectCreate(self, pos, image) -> pygame.Rect:
        return pygame.Rect(pos[0], pos[1], image.get_width(), image.get_height())