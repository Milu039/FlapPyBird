from ..utils import GameConfig
from .entity import Entity


class Floor(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(config, config.images.base, 0, config.window.vh)
        self.vel_x = 8
        self.x_extra = self.w - config.window.w

    def stop(self) -> None:
        self.vel_x = 0

    def resume(self) -> None:
        self.vel_x = 8
        
    def draw(self) -> None:
        self.x = -((-self.x + self.vel_x) % self.x_extra)
        super().draw()
