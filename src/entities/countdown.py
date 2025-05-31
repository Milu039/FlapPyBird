# countdown_timer.py
import time
import pygame
from ..utils import GameConfig
from .entity import Entity

class CountdownTimer(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(config)
        self.countdown_duration = 3  # 3 seconds
        self.start_time = time.time()
        self.remaining_time = self.countdown_duration
        
        # Create transparent overlay surface with per-pixel alpha
        self.overlay = pygame.Surface((self.config.window.width, self.config.window.height), pygame.SRCALPHA)
        # Fill with black color at 75% opacity (alpha 191 out of 255)
        self.overlay.fill((0, 0, 0, 25))  # RGBA: Black with 75% opacity
        
        # Font for countdown numbers
        self.font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 200)  # Large font for countdown

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

    def get_countdown_number(self) -> int:
        """Get the current countdown number (3, 2, 1)"""
        self.update_countdown()
        return self.remaining_time if self.remaining_time > 0 else 0

    def draw(self) -> None:
        """Draw the countdown with transparent black overlay"""
        number = self.get_countdown_number()
        
        if number > 0:
            # Draw transparent black overlay
            self.config.screen.blit(self.overlay, (0, 0))
            
            # Draw countdown number at center
            number_text = self.font.render(str(number), True, (255, 255, 255))  # White text
            number_rect = number_text.get_rect(
                center=(self.config.window.width // 2, self.config.window.height // 2)
            )
            self.config.screen.blit(number_text, number_rect)

    def pause_with_countdown(self) -> None:
        """Pause the game for 3 seconds with countdown display"""
        self.reset()  # Reset timer to start countdown
        
        while not self.is_finished():
            # Handle quit events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            # Keep drawing your game background first (this preserves what's underneath)
            # Note: You'll need to call your game's draw methods here to see through the overlay
            
            # Draw the countdown overlay and number on top
            self.draw()
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            self.config.tick()

# Standalone function for easy use
def pause_with_countdown(config: GameConfig) -> None:
    """Simple function to pause with 3-second countdown"""
    countdown = CountdownTimer(config)
    countdown.pause_with_countdown()