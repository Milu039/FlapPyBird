from ..utils import GameConfig
from .entity import Entity

class ScoreBoard(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(
            config=config,
            image=config.images.scoreboard,
            x=(config.window.width - config.images.scoreboard.get_width()) // 2,
            y=int(config.window.height - config.images.scoreboard.get_height()) // 2 - 50,
        )