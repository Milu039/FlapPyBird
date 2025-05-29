import time
from ..utils import GameConfig
from .entity import Entity
from .player import Player

class Timer(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(config)
        self.y = self.config.window.height * 0.1
        self.total_time = 1 * 300  # 5 minutes in seconds
        self.start_time = time.time()
        self.remaining_time = self.total_time

    def reset(self) -> None:
        self.start_time = time.time()
        self.remaining_time = self.total_time

    def update_timer(self) -> None:
        elapsed = time.time() - self.start_time
        self.remaining_time = max(0, self.total_time - int(elapsed))

    def time_up(self) -> bool:
        self.update_timer()
        return self.remaining_time <= 0

    def get_time_digits(self) -> list:
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_str = f"{minutes:02d}{seconds:02d}"
        return [int(ch) for ch in time_str]

    def draw_timer(self) -> None:

        digits = self.get_time_digits()
        images = [self.config.images.numbers[d] for d in digits]

        total_width = sum(img.get_width() for img in images)
        x_offset = (self.config.window.width - total_width) / 2

        for image in images:
            self.config.screen.blit(image, (x_offset, self.y))
            x_offset += image.get_width()

    def draw(self) -> None:
        self.draw_timer()
