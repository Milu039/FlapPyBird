import pygame
import os
from ..utils import GameConfig
from .entity import Entity
from .player import Player, PlayerMode

class Score(Entity):
    def __init__(self, config: GameConfig, player: Player) -> None:
        super().__init__(config)
        self.player = player
        self.best_score_file_path = "assets/data/best_score.txt"
        self.best_score = self.read_best_score()
        self.y = self.config.window.height * 0.1
        self.score = 0

    def reset(self) -> None:
        self.score = 0

    def add(self) -> None:
        self.score += 1
        self.config.sounds.point.play()
    
    def read_best_score(self) -> int:
        try:
            with open(self.best_score_file_path, "r") as f:
                return int(f.read().strip() or 0)
        except FileNotFoundError:
            return 0

    def write_best_score(self) -> None:
        with open(self.best_score_file_path, "w") as f:
            f.write(str(self.best_score))

    @property
    def rect(self) -> pygame.Rect:
        score_digits = [int(x) for x in list(str(self.score))]
        images = [self.config.images.numbers[digit] for digit in score_digits]
        w = sum(image.get_width() for image in images)
        x = (self.config.window.width - w) / 2
        h = max(image.get_height() for image in images)
        return pygame.Rect(x, self.y, w, h)

    def draw_score(self,score: int, y_offset: float):
            digits = [int(d) for d in str(score)]
            images = [self.config.images.numbers[d] for d in digits]
            x_offset = (self.config.window.width - sum(img.get_width() for img in images)) / 2 + 150
            for image in images:
                self.config.screen.blit(image, (x_offset, y_offset))
                x_offset += image.get_width()

    def draw(self) -> None:
        """displays score in center of screen"""
        if(self.player.mode == PlayerMode.NORMAL or self.player.mode == PlayerMode.PAUSE):
            score_digits = [int(d) for d in list(str(self.score))]
            images = [self.config.images.numbers[digit] for digit in score_digits]
            digits_width = sum(image.get_width() for image in images)
            x_offset = (self.config.window.width - digits_width) / 2

            for image in images:
                self.config.screen.blit(image, (x_offset, self.y))
                x_offset += image.get_width()

        elif self.player.mode == PlayerMode.CRASH:
            # Update best score
            if self.score > self.best_score:
                self.best_score = self.score
                self.write_best_score()

            self.draw_score(self.score, self.y + 215)         # Gained score
            self.draw_score(self.best_score, self.y + 290)    # Best score


