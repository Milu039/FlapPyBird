import pygame
import random
from enum import Enum
from typing import Optional, Dict, List
from ..utils import GameConfig
from .entity import Entity

class SkillType(Enum):
    SPEED_BOOST = "speed_boost"
    PENETRATION = "penetration"

class SkillState(Enum):
    INACTIVE = "inactive"  # No skill available
    AVAILABLE = "available"  # Skill ready to use
    ACTIVE = "active"  # Skill currently in use

class Skill(Entity):
    def __init__(self, config: GameConfig, skill_type: SkillType, player_id: int) -> None:
        # Initialize with the skill icon image
        image = config.images.skills[skill_type.value]
        # Position skill icon at bottom center of screen
        x = 50 - image.get_width() // 2
        y = config.window.height - 130
        
        super().__init__(config, image, x, y)
        
        self.skill_type = skill_type
        self.player_id = player_id
        self.state = SkillState.INACTIVE
        
        # Skill parameters
        self.duration = 0  # Duration in frames
        self.active_timer = 0
        
        # Set skill-specific parameters
        self._setup_skill_params()
        
        # Speed boost specific variables
        self.speed_boost_amount = 0
        self.original_x = 0
        
        # Penetration specific
        self.penetration_active = False
        
    def _setup_skill_params(self) -> None:
        """Set up duration for each skill type"""
        if self.skill_type == SkillType.SPEED_BOOST:
            self.duration = 150  # 5 seconds at 30 FPS
            self.speed_boost_amount = 3  # Extra pixels per frame
        elif self.skill_type == SkillType.PENETRATION:
            self.duration = 90   # 3 seconds
            
    def grant_skill(self) -> None:
        """Grant this skill to the player"""
        if self.state == SkillState.INACTIVE:
            self.state = SkillState.AVAILABLE
    
    def activate(self, player, game_state: Optional[Dict] = None) -> bool:
        """Activate the skill if available"""
        if self.state != SkillState.AVAILABLE:
            return False
            
        self.state = SkillState.ACTIVE
        self.active_timer = self.duration
        
        # Apply skill effect based on type
        if self.skill_type == SkillType.SPEED_BOOST:
            self._activate_speed_boost(player)
        elif self.skill_type == SkillType.PENETRATION:
            self._activate_penetration(player)
        
        return True
    
    def _activate_speed_boost(self, player) -> None:
        """Activate speed boost for the player"""
        # Store original velocity if player has velocity_x attribute
        if hasattr(player, 'velocity_x'):
            self.original_velocity_x = player.vel_x
            player.vel_x += self.speed_boost_amount
        else:
            # Create velocity_x attribute if it doesn't exist
            player.vel_x = self.speed_boost_amount
            self.original_velocity_x = 0
        
    def _activate_penetration(self, player) -> None:
        """Activate penetration - player can pass through pipes"""
        self.penetration_active = True
        
    def update(self, player, pipes=None, game_state: Optional[Dict] = None) -> None:
        """Update skill state and effects"""
        if self.state == SkillState.ACTIVE:
            self.active_timer -= 1
            
            # Apply ongoing effects
            if self.skill_type == SkillType.SPEED_BOOST:
                # Speed boost is handled by velocity, no need to update here
                pass
            elif self.skill_type == SkillType.PENETRATION:
                self._update_penetration(player)
            
            # Check if skill duration has ended
            if self.active_timer <= 0:
                self._deactivate(player)
    
    def _update_speed_boost(self, player) -> None:
        """Apply speed boost effect to player"""
        # Now handled by player's velocity_x
        pass
        
    def _update_penetration(self, player) -> None:
        """Handle penetration effect"""
        # The actual collision ignore logic would be in the player's collision detection
        pass
        
    def _deactivate(self, player) -> None:
        """Deactivate skill and remove from player"""
        self.state = SkillState.INACTIVE
        self.active_timer = 0
        
        # Remove any ongoing effects
        if self.skill_type == SkillType.PENETRATION:
            self.penetration_active = False
        elif self.skill_type == SkillType.SPEED_BOOST:
            # Restore original velocity
            if hasattr(player, 'velocity_x'):
                player.vel_x = self.original_velocity_x if hasattr(self, 'original_velocity_x') else 0
    
    def draw(self) -> None:
        """Draw skill icon only if available or active"""
        if self.state == SkillState.INACTIVE:
            return
            
        # Draw skill icon
        super().draw()
        
        # Draw active indicator
        if self.state == SkillState.ACTIVE:
            # Draw glowing border
            pygame.draw.rect(self.config.screen, (255, 255, 0), 
                           (self.x - 2, self.y - 2, self.w + 4, self.h + 4), 2)
            
            # Show remaining duration
            if self.duration > 1:  # Only show timer for non-instant skills
                duration_text = f"{self.active_timer // 30}"  # Convert to seconds
                font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 12)
                text_surface = font.render(duration_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(self.x + self.w // 2, self.y + self.h // 2))
                self.config.screen.blit(text_surface, text_rect)
        elif self.state == SkillState.AVAILABLE:
            # Draw ready indicator (subtle pulse effect)
            pulse = abs((pygame.time.get_ticks() % 1000) - 500) / 500
            alpha = int(100 + 155 * pulse)
            s = pygame.Surface((self.w + 4, self.h + 4))
            s.set_alpha(alpha)
            s.fill((100, 255, 100))
            self.config.screen.blit(s, (self.x - 2, self.y - 2))
    
    def is_available(self) -> bool:
        """Check if skill can be activated"""
        return self.state == SkillState.AVAILABLE
    
    def is_active(self) -> bool:
        """Check if skill is currently active"""
        return self.state == SkillState.ACTIVE
    
    def reset(self) -> None:
        """Reset skill to initial state"""
        self.state = SkillState.INACTIVE
        self.active_timer = 0
        self.penetration_active = False


class SkillManager:
    """Manages skill distribution and usage for a player"""
    def __init__(self, config: GameConfig, player_id: int) -> None:
        self.config = config
        self.player_id = player_id
        
        # Current skill slot (only one skill at a time)
        self.current_skill: Optional[Skill] = None
        
        # Skill distribution timer
        self.skill_distribution_timer = 0
        self.skill_distribution_interval = 150  # 5 seconds at 30 FPS
        
        # Next skill distribution time
        self.next_distribution_time = self.skill_distribution_interval
        
        # Available skill types
        self.available_skill_types = list(SkillType)
        
    def update(self, player, pipes=None, game_state: Optional[Dict] = None) -> None:
        """Update skill manager and current skill"""
        # Update distribution timer
        self.skill_distribution_timer += 1
        
        # Check if it's time to distribute a new skill
        if self.skill_distribution_timer >= self.next_distribution_time:
            self.distribute_random_skill()
            # Reset timer for next distribution
            self.skill_distribution_timer = 0
            self.next_distribution_time = self.skill_distribution_interval
        
        # Update current skill if exists
        if self.current_skill:
            self.current_skill.update(player, pipes, game_state)
            
            # Remove skill if it's no longer active
            if self.current_skill.state == SkillState.INACTIVE:
                self.current_skill = None
    
    def distribute_random_skill(self) -> None:
        """Randomly give a skill to the player"""
        # Only distribute if player doesn't have an active skill
        if self.current_skill and self.current_skill.state == SkillState.ACTIVE:
            return
            
        # Choose a random skill type
        skill_type = random.choice(self.available_skill_types)
        
        # Create new skill
        self.current_skill = Skill(self.config, skill_type, self.player_id)
        self.current_skill.grant_skill()
        
        print(f"Player {self.player_id} received {skill_type.value} skill!")
    
    def activate_skill(self, player, game_state: Optional[Dict] = None) -> bool:
        """Activate the current skill if available"""
        if self.current_skill and self.current_skill.is_available():
            return self.current_skill.activate(player, game_state)
        return False
    
    def draw(self) -> None:
        """Draw current skill icon"""
        if self.current_skill:
            self.current_skill.draw()
    
    def handle_key_press(self, key: int, player, game_state: Optional[Dict] = None) -> None:
        """Handle keyboard input for skills"""
        if key == pygame.K_1:
            self.activate_skill(player, game_state)
    
    def has_penetration_active(self) -> bool:
        """Check if penetration skill is currently active"""
        return (self.current_skill and 
                self.current_skill.skill_type == SkillType.PENETRATION and 
                self.current_skill.penetration_active)
    
    def reset(self) -> None:
        """Reset skill manager"""
        self.current_skill = None
        self.skill_distribution_timer = 0
        self.next_distribution_time = self.skill_distribution_interval