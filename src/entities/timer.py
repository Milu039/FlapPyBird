import time
import pygame
from ..utils import GameConfig
from .entity import Entity

class Timer(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(config)
        self.y = self.config.window.height * 0.1
        self.total_time = 1 * 300  # 5 minutes in seconds
        self.start_time = None
        self.remaining_time = self.total_time
        self.colon_image = pygame.font.SysFont(None, 48).render(":", True, (255, 255, 255))

    def start(self):
        self.start_time = time.time()

    def reset(self) -> None:
        self.start_time = time.time()
        self.remaining_time = self.total_time

    def update_timer(self) -> None:
        elapsed = time.time() - self.start_time
        self.remaining_time = max(0, self.total_time - int(elapsed))

    def time_up(self) -> bool:
        self.update_timer()
        return time.time() - self.start_time >= self.total_time

    def get_time_digits(self) -> list:
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_str = f"{minutes:02d}{seconds:02d}"
        return [int(ch) for ch in time_str]

    def draw_timer(self) -> None:
        digits = self.get_time_digits()  # Returns [0, 5, 0, 0]
        digit_images = [self.config.images.numbers[d] for d in digits]

        # Create colon with black outline
        font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 48)
        colon_color = (255, 255, 255)
        outline_color = (0, 0, 0)

        colon_surface = font.render(":", True, colon_color)
        outline_surfaces = [
            (font.render(":", True, outline_color), dx, dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        ]

        # Compute total width including colon
        total_width = (
            digit_images[0].get_width() +
            digit_images[1].get_width() +
            colon_surface.get_width() +
            digit_images[2].get_width() +
            digit_images[3].get_width()
        )

        x_offset = (self.config.window.width - total_width) / 2
        y = self.y

        # Draw first two digits
        self.config.screen.blit(digit_images[0], (x_offset, y))
        x_offset += digit_images[0].get_width()

        self.config.screen.blit(digit_images[1], (x_offset, y))
        x_offset += digit_images[1].get_width()

        # Draw colon outline (behind)
        for surf, dx, dy in outline_surfaces:
            self.config.screen.blit(surf, (x_offset + dx, y + dy))

        # Draw colon foreground
        self.config.screen.blit(colon_surface, (x_offset, y))
        x_offset += colon_surface.get_width()

        # Draw last two digits
        self.config.screen.blit(digit_images[2], (x_offset, y))
        x_offset += digit_images[2].get_width()

        self.config.screen.blit(digit_images[3], (x_offset, y))

    def draw(self) -> None:
        self.draw_timer()
