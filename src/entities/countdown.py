# countdown_timer.py
import time
import pygame
from ..utils import GameConfig
from .entity import Entity

class CountdownTimer(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(config)
        self.y = self.config.window.height * 0.4  # Center vertically
        self.countdown_duration = 3  # 3 seconds
        self.start_time = time.time()
        self.remaining_time = self.countdown_duration

    def reset(self) -> None:
        """Reset the countdown timer"""
        self.start_time = time.time()
        self.remaining_time = self.countdown_duration

    def update_countdown(self) -> None:
        """Update the remaining countdown time"""
        elapsed = time.time() - self.start_time
        self.remaining_time = max(0, self.countdown_duration - int(elapsed))

    def is_finished(self) -> bool:
        """Check if countdown has finished"""
        self.update_countdown()
        return self.remaining_time <= 0

    def get_countdown_digit(self) -> int:
        """Get the current countdown number (3, 2, 1)"""
        self.update_countdown()
        return max(1, self.remaining_time) if self.remaining_time > 0 else 0

    def draw_countdown(self) -> None:
        """Draw the countdown number centered on screen"""
        digit = self.get_countdown_digit()
        
        if digit > 0:
            # Get the number image
            number_image = self.config.images.numbers[digit]
            
            # Center the number on screen
            x_pos = (self.config.window.width - number_image.get_width()) / 2
            
            # Draw the countdown number
            self.config.screen.blit(number_image, (x_pos, self.y))

    def draw(self) -> None:
        """Main draw method"""
        self.draw_countdown()

    def pause_with_countdown(config: GameConfig) -> None:
        countdown = CountdownTimer(config)
        # Main countdown loop
        while not countdown.is_finished():
            # Handle events (optional - allows quitting during countdown)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            # Clear screen (you might want to draw your paused game state here)
            config.screen.fill((0, 0, 0))  # Black background
            
            # Draw countdown
            countdown.draw()
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            config.tick()

