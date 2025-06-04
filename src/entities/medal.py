import pygame
from ..utils import GameConfig
from .entity import Entity
from .score import Score

class Medal(Entity):
    def __init__(self, config: GameConfig, score: Score) -> None:
        super().__init__(config)
        self.score_ref = score
        self.mode = "solo"
        # set default position of medal
        self.x = 389.5
        self.y = 349

    def set_mode(self, mode: str):
        assert mode in ("solo", "multi")
        self.mode = mode

    def draw(self, ):
        if self.mode == "solo":
            # draw image based on score gained
            current_score = self.score_ref.score
            image = None
            if current_score >= 40:
                image = self.config.images.medals["plat"]
            elif current_score >= 30:
                image = self.config.images.medals["gold"]
            elif current_score >= 20:
                image = self.config.images.medals["silver"]
            elif current_score >= 10:
                image = self.config.images.medals["bronze"]

            if image:
                self.config.screen.blit(
                    image,
                    image.get_rect(center=(self.x, self.y))
                )
        elif self.mode == "multi":
            gold_medal = self.config.images.medals["gold"]
            silver_medal = self.config.images.medals["silver"]
            bronze_medal = self.config.images.medals["bronze"]

            pos_gold_medal = (int(self.config.window.width - gold_medal.get_width()) // 2 - 5, int(self.config.window.height - gold_medal.get_height()) // 2 - 175)
            pos_silver_medal =  (int(self.config.window.width - silver_medal.get_width()) // 2 - 150, int(self.config.window.height - silver_medal.get_height()) // 2 - 135)
            pos_bronze_medal =  (int(self.config.window.width - bronze_medal.get_width()) // 2 + 140, int(self.config.window.height - bronze_medal.get_height()) // 2 - 95)

            self.config.screen.blit(gold_medal,pos_gold_medal)
            self.config.screen.blit(silver_medal,pos_silver_medal)
            self.config.screen.blit(bronze_medal,pos_bronze_medal)

