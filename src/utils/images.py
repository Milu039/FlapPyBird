import random
from typing import List, Tuple

import pygame

from .constants import PLAYERS


class Images:
    numbers: List[pygame.Surface]
    icon: dict
    scoreboard: pygame.Surface
    message: dict
    container: dict
    base: pygame.Surface
    background: pygame.Surface
    player: Tuple[pygame.Surface]
    pipe: pygame.Surface
    medals: dict
    buttons: dict
    title: dict
    skin: Tuple[pygame.Surface]

    def __init__(self) -> None:
        self.numbers = list(
            (
                pygame.image.load(f"assets/sprites/{num}.png").convert_alpha()
                for num in range(10)
            )
        )

        self.icon = {
            "host": pygame.image.load("assets/sprites/host_icon.png").convert_alpha(),
            "kick": pygame.image.load("assets/sprites/kick_icon.png").convert_alpha(),
            "ready": pygame.image.load("assets/sprites/ready_icon.png").convert_alpha()
        }
        # title sprite
        self.title = pygame.image.load(
            "assets/sprites/title.png"
        ).convert_alpha()

        self.background = pygame.image.load("assets/sprites/background-day.png")

        # message sprite
        self.message = {
            "ready": pygame.image.load("assets/sprites/message.png").convert_alpha(),
            "game room": pygame.image.load("assets/sprites/Game room.png").convert_alpha(),
            "create": pygame.image.load("assets/sprites/Create room.png").convert_alpha(),
            "gameover": pygame.image.load("assets/sprites/gameover.png").convert_alpha(),
            "leaderboard": pygame.image.load("assets/sprites/Leaderboard.png").convert_alpha(),
            "skill_ability": pygame.image.load("assets/sprites/skill_ability.png").convert_alpha(),
        }

        original_container = pygame.image.load("assets/sprites/container.png").convert_alpha()
        leaderboard_container = pygame.image.load("assets/sprites/leaderboard container.png").convert_alpha()
        message_box = pygame.transform.scale(original_container, (350,275))
        room_list_container = pygame.transform.scale(original_container, (700,500))
        create_room_container = pygame.transform.scale(original_container, (400,400))
        room_lobby_container = pygame.transform.scale(original_container, (500,400))
        resize_leaderboard_container = pygame.transform.scale(leaderboard_container, (600,500))
        self.container = {
            "message box" : message_box,
            "room list": room_list_container,
            "create room": create_room_container,
            "room lobby": room_lobby_container,
            "leaderboard": resize_leaderboard_container
        }
        
        # base (ground) sprite
        self.base = pygame.image.load("assets/sprites/base.png").convert_alpha()

        # scoreboard sprite
        self.scoreboard = pygame.image.load(
            "assets/sprites/scoreboard.png"
        ).convert_alpha()

        # medals sprite
        self.medals = {
            "bronze": pygame.image.load("assets/sprites/bronze.png").convert_alpha(),
            "silver": pygame.image.load("assets/sprites/silver.png").convert_alpha(),
            "gold": pygame.image.load("assets/sprites/gold.png").convert_alpha(),
            "plat": pygame.image.load("assets/sprites/plat.png").convert_alpha(),
        }

        # buttons sprite
        self.buttons = {
            "back": pygame.image.load("assets/sprites/back.png").convert_alpha(),
            "resume": pygame.image.load("assets/sprites/resume.png").convert_alpha(),
            "restart": pygame.image.load("assets/sprites/restart.png").convert_alpha(),
            "quit": pygame.image.load("assets/sprites/quit.png").convert_alpha(),
            "join": pygame.image.load("assets/sprites/join.png").convert_alpha(),
            "enter": pygame.image.load("assets/sprites/enter.png").convert_alpha(),
            "cancel": pygame.image.load("assets/sprites/cancel.png").convert_alpha(),
            "create": pygame.image.load("assets/sprites/create.png").convert_alpha(),
            "next": pygame.image.load("assets/sprites/next-skin.png").convert_alpha(),
            "previous": pygame.image.load("assets/sprites/previous-skin.png").convert_alpha(),
            "start (1/4)": pygame.image.load("assets/sprites/start-1-4.png").convert_alpha(),
            "start (2/4)": pygame.image.load("assets/sprites/start-2-4.png").convert_alpha(),
            "start (3/4)": pygame.image.load("assets/sprites/start-3-4.png").convert_alpha(),
            "start": pygame.image.load("assets/sprites/start.png").convert_alpha(),
            "ready": pygame.image.load("assets/sprites/ready.png").convert_alpha(),
        }

        # Each entry = (upflap, midflap, downflap)
        self.skin = [
            (
                pygame.image.load("assets/sprites/yellowbird-upflap.png").convert_alpha(),
                pygame.image.load("assets/sprites/yellowbird-midflap.png").convert_alpha(),
                pygame.image.load("assets/sprites/yellowbird-downflap.png").convert_alpha(),
            ),
            (
                pygame.image.load("assets/sprites/greenbird-upflap.png").convert_alpha(),
                pygame.image.load("assets/sprites/greenbird-midflap.png").convert_alpha(),
                pygame.image.load("assets/sprites/greenbird-downflap.png").convert_alpha(),
            ),
            (
                pygame.image.load("assets/sprites/redbird-upflap.png").convert_alpha(),
                pygame.image.load("assets/sprites/redbird-midflap.png").convert_alpha(),
                pygame.image.load("assets/sprites/redbird-downflap.png").convert_alpha(),
            ),
            (
                pygame.image.load("assets/sprites/bluebird-upflap.png").convert_alpha(),
                pygame.image.load("assets/sprites/bluebird-midflap.png").convert_alpha(),
                pygame.image.load("assets/sprites/bluebird-downflap.png").convert_alpha(),
            ),
            (
                pygame.image.load("assets/sprites/unknow-flappy.png").convert_alpha(),
            ),
        ]

        self.skills = {
            "speed_boost": pygame.image.load("assets/sprites/speed_boost.png").convert_alpha(),
            "penetration": pygame.image.load("assets/sprites/penetration.png").convert_alpha(),
            "pipe_shift": pygame.image.load("assets/sprites/pipe_shift.png").convert_alpha(),
            "time_freeze": pygame.image.load("assets/sprites/time_freeze.png").convert_alpha(),
            "teleport": pygame.image.load("assets/sprites/teleport.png").convert_alpha(),
        }

        self.randomize()

    def randomize(self):
        # select random player sprites
        rand_player = random.randint(0, len(PLAYERS) - 1)

        self.player = (
            pygame.image.load(PLAYERS[rand_player][0]).convert_alpha(),
            pygame.image.load(PLAYERS[rand_player][1]).convert_alpha(),
            pygame.image.load(PLAYERS[rand_player][2]).convert_alpha(),
        )

        self.pipe = (
            pygame.transform.flip(
                pygame.image.load("assets/sprites/pipe-green.png").convert_alpha(),
                False,
                True,
            ),
            pygame.image.load("assets/sprites/pipe-green.png").convert_alpha(),
        )
