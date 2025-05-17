from ..utils import GameConfig
from .entity import Entity

class Title(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(
            config=config,
            image=config.images.title,
            x=(config.window.width - config.images.title.get_width()) // 2,
            y=int(config.window.height * 0.01),
        )