import pygame
from ..utils import GameConfig, Mode
from .entity import Entity

class Container(Entity):
    def __init__(self, config: GameConfig, mode: Mode) -> None:
        super().__init__(config)
        self.FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 12)
        self.BLACK = (0,0,0)
        self.mode = mode
        self.conRoomList= config.images.container["room list"]
        self.conCreateRoom = config.images.container["create room"]
        self.conRoomLobby = config.images.container["room lobby"]

    def set_mode(self,mode):
        self.mode = mode

    def draw_container(self, con, pos):
        self.config.screen.blit(con, pos)

    def draw(self):
        if self.mode == "Game Room":
            self.posRoomList = (
                int(self.config.window.width - self.conRoomList.get_width()) // 2, 
                int(self.config.window.height - self.conRoomList.get_height()) // 2
                )
            self.draw_container(self.conRoomList, self.posRoomList)

        elif self.mode == "Create Room":
            self.posCreateRoom = (
                int(self.config.window.width - self.conCreateRoom.get_width()) // 2,
                int(self.config.window.height - self.conCreateRoom.get_height()) // 2
            )
            self.draw_container(self.conCreateRoom, self.posCreateRoom)

        elif self.mode == "Room Lobby: host" or "Room Lobby: member":
            self.posRoomLobby = (
                int(self.config.window.width - self.conRoomLobby.get_width()) // 2,
                int(self.config.window.height - self.conRoomLobby.get_height()) // 2 - 50
            )
            self.draw_container(self.conRoomLobby, self.posRoomLobby)
            
        

