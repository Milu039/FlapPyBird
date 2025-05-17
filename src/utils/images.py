import random
from typing import List, Tuple

import pygame

from .constants import BACKGROUNDS, PLAYERS


class Images:
    numbers: List[pygame.Surface]
    game_over: pygame.Surface
    scoreboard: pygame.Surface
    welcome_message: pygame.Surface
    base: pygame.Surface
    background: pygame.Surface
    player: Tuple[pygame.Surface]
    pipe: pygame.Surface
    medals: dict
    buttons: dict
    title: pygame.Surface

    def __init__(self, screen_width, screen_height) -> None:
        self.numbers = list(
            (
                pygame.image.load(f"assets/sprites/{num}.png").convert_alpha()
                for num in range(10)
            )
        )
        # title sprite
        self.title = pygame.image.load(
            "assets/sprites/title.png"
        ).convert_alpha()

        # game over sprite
        self.game_over = pygame.image.load(
            "assets/sprites/gameover.png"
        ).convert_alpha()

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
            "restart": pygame.image.load("assets/sprites/restart.png").convert_alpha(),
            "quit": pygame.image.load("assets/sprites/quit.png").convert_alpha(),
        }

        # welcome_message sprite for welcome screen
        self.welcome_message = pygame.image.load(
            "assets/sprites/message.png"
        ).convert_alpha()
        # base (ground) sprite
        self.base = pygame.image.load("assets/sprites/base.png").convert_alpha()

        self.randomize()

    def randomize(self):
        # select random background sprites
        rand_bg = random.randint(0, len(BACKGROUNDS) - 1)
        # select random player sprites
        rand_player = random.randint(0, len(PLAYERS) - 1)

        self.background = pygame.image.load(BACKGROUNDS[rand_bg]).convert()
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
