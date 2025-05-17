from ..utils import GameConfig
from .entity import Entity
from .score import Score

class Medal(Entity):
    def __init__(self, config: GameConfig, score: Score) -> None:
        super().__init__(config)
        self.score_ref = score
        # set default position of medal
        self.x = 389.5
        self.y = 349

    def draw(self):
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
