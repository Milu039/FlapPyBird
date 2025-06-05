from enum import Enum
from itertools import cycle

import pygame

from ..utils import GameConfig, clamp
from .entity import Entity
from .floor import Floor
from .pipe import Pipe, Pipes


class PlayerMode(Enum):
    SHM = "SHM"
    NORMAL = "NORMAL"
    PAUSE = "PAUSE"
    CRASH = "CRASH"
    MULTI = "MULTI"

class Player(Entity):
    def __init__(self, config: GameConfig) -> None:
        image = config.images.player[0]
        x = int(config.window.width * 0.2)
        y = int((config.window.height - image.get_height()) / 2)
        super().__init__(config, image, x, y)
        self.min_y = -2 * self.h
        self.max_y = config.window.viewport_height - self.h * 0.75
        self.img_idx = 0
        self.img_gen = cycle([0, 1, 2, 1])
        self.frame = 0
        self.id = 0
        self.skin_id = 0
        self.respawn_timer = 0
        self.respawn_delay = 24
        self.waiting_to_respawn = False
        self.vel_x = 0
        
        # Post-respawn transparency
        self.respawn_grace_period = 120  # 2 seconds of transparency after respawn
        self.respawn_grace_timer = 0
        self.just_respawned = False
        
        self.crashed = False
        self.crash_entity = None
        self.set_mode(PlayerMode.SHM)

    def set_mode(self, mode: PlayerMode) -> None:
        self.mode = mode
        if mode == PlayerMode.NORMAL:
            self.reset_vals_normal()
            self.config.sounds.wing.play()
            self.resume_wings()
        elif mode == PlayerMode.SHM:
            self.reset_vals_shm()
        elif mode == PlayerMode.PAUSE:
            self.stop_wings()
        elif mode == PlayerMode.CRASH:
            self.stop_wings()
            self.config.sounds.hit.play()
            if self.crash_entity == "pipe":
                self.config.sounds.die.play()
            self.reset_vals_crash()
        elif mode == PlayerMode.MULTI:
            self.reset_vals_multi()
            self.resume_wings()
            
    def get_own_state(self):
        return self.x, self.y, self.rot
    
    def reset(self) -> None:
        """Reset player to initial state before a new multiplayer game."""
        self.x = int(self.config.window.width * 0.2)
        self.y = int((self.config.window.height - self.h) / 2)
        self.vel_y = 0
        self.rot = 0
        self.frame = 0
        self.img_idx = 0
        self.img_gen = cycle([0, 1, 2, 1])
        self.flapped = False
        self.vel_x = 0
        
        # Reset boundaries
        self.min_y = -2 * self.h
        self.max_y = self.config.window.viewport_height - self.h * 0.75

        # Reset gameplay flags
        self.crashed = False
        self.crash_entity = None

        # Reset respawn-related states
        self.respawn_timer = 0
        self.respawn_delay = 24
        self.waiting_to_respawn = False
        self.respawn_grace_timer = 0
        self.just_respawned = False

        # Resume animation
        self.resume_wings()

        # Reset to MULTI mode by default
        self.set_mode(PlayerMode.MULTI)
        
    def reset_vals_normal(self) -> None:
        self.vel_y = -9  # player's velocity along Y axis
        self.max_vel_y = 10  # max vel along Y, max descend speed
        self.min_vel_y = -8  # min vel along Y, max ascend speed
        self.acc_y = 1  # players downward acceleration

        self.rot = 80  # player's current rotation
        self.vel_rot = -3  # player's rotation speed
        self.rot_min = -90  # player's min rotation angle
        self.rot_max = 20  # player's max rotation angle

        self.flap_acc = -9  # players speed on flapping
        self.flapped = False  # True when player flaps

    def reset_vals_shm(self) -> None:
        self.vel_y = 1  # player's velocity along Y axis
        self.max_vel_y = 4  # max vel along Y, max descend speed
        self.min_vel_y = -4  # min vel along Y, max ascend speed
        self.acc_y = 0.5  # players downward acceleration

        self.rot = 0  # player's current rotation
        self.vel_rot = 0  # player's rotation speed
        self.rot_min = 0  # player's min rotation angle
        self.rot_max = 0  # player's max rotation angle

        self.flap_acc = 0  # players speed on flapping
        self.flapped = False  # True when player flaps

    def reset_vals_crash(self) -> None:
        self.acc_y = 2
        self.vel_y = 7
        self.max_vel_y = 15
        self.vel_rot = -8
        
    def reset_vals_multi(self) -> None:
        """Reset values for multiplayer mode - similar to normal but with respawn"""
        self.vel_y = -9  # player's velocity along Y axis
        self.max_vel_y = 10  # max vel along Y, max descend speed
        self.min_vel_y = -8  # min vel along Y, max ascend speed
        self.vel_x = 0 # vel x 
        self.acc_y = 1  # players downward acceleration

        self.rot = 80  # player's current rotation
        self.vel_rot = -3  # player's rotation speed
        self.rot_min = -90  # player's min rotation angle
        self.rot_max = 20  # player's max rotation angle

        self.flap_acc = -9  # players speed on flapping
        self.flapped = False  # True when player flaps
        
        # Reset respawn-related flags
        self.waiting_to_respawn = False
        self.just_respawned = False
        self.respawn_timer = 0
        self.respawn_grace_timer = 0
    
    def update_image(self):
        self.frame += 1
        if self.frame % 5 == 0:
            self.img_idx = next(self.img_gen)
            if self.mode == PlayerMode.MULTI:
                # Use skin images in MULTI mode
                self.image = self.config.images.skin[self.skin_id][self.img_idx]
            else:
                # Use default player images in other modes
                self.image = self.config.images.player[self.img_idx]
            self.w = self.image.get_width()
            self.h = self.image.get_height()

    def tick_shm(self) -> None:
        if self.vel_y >= self.max_vel_y or self.vel_y <= self.min_vel_y:
            self.acc_y *= -1
        self.vel_y += self.acc_y
        self.y += self.vel_y

    def tick_normal(self) -> None:
        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False

        self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
        self.rotate()

    def tick_crash(self) -> None:
        if self.min_y <= self.y <= self.max_y:
            self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
            # rotate only when it's a pipe crash and bird is still falling
            if self.crash_entity != "floor":
                self.rotate()

        # player velocity change
        if self.vel_y < self.max_vel_y:
            self.vel_y += self.acc_y

    def tick_multi(self) -> None:
        """Update player position and state in MULTI mode"""
        # Apply horizontal velocity if in MULTI mode
        if self.mode == PlayerMode.MULTI and hasattr(self, 'velocity_x'):
            self.x += self.velocity_x
        # Same physics as normal mode
        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False

        self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
        self.rotate()
    
    def rotate(self) -> None:
        self.rot = clamp(self.rot + self.vel_rot, self.rot_min, self.rot_max)

    def draw(self) -> None:
        self.update_image()
        if self.mode == PlayerMode.SHM:
            self.tick_shm()
        elif self.mode == PlayerMode.NORMAL:
            self.tick_normal()
        elif self.mode == PlayerMode.MULTI:
            self.tick_multi()
        elif self.mode == PlayerMode.CRASH:
            self.tick_crash()

        self.draw_player()

    def draw_player(self) -> None:
        # Don't draw player while waiting to respawn (only in MULTI mode)
        if self.mode == PlayerMode.MULTI and self.waiting_to_respawn:
            return
        
        rotated_image = pygame.transform.rotate(self.image, self.rot)
        
        # Make player semi-transparent after respawning (only in MULTI mode)
        if self.mode == PlayerMode.MULTI and self.just_respawned:
            # Blinking effect: alternate between normal and transparent
            if (self.respawn_grace_timer // 10) % 2 == 0:
                return
            else:
                rotated_image.set_alpha(255)  # Full opacity
        
        rotated_image = pygame.transform.rotate(self.image, self.rot)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        self.config.screen.blit(rotated_image, rotated_rect)

    def draw_other(self, players):
        for i, player in enumerate(players):
            if player is None:
                continue

            player_id = player.get("player_id")
            skin_id = player.get("skin_id")
            x = player.get("x")
            y = player.get("y")
            rot = player.get("rot", 0)

            # Use the current frame to animate (e.g., same frame cycle logic)
            frame_idx = self.img_idx  # Sync animation frame with main player
            image = self.config.images.skin[skin_id][frame_idx]

            # Only draw bird if it's not this client player
            if player_id != self.id:
                rotated_image = pygame.transform.rotate(image, rot)
                rect = rotated_image.get_rect(center=(x + image.get_width() // 2, y + image.get_height() // 2))
                self.config.screen.blit(rotated_image, rect)

            # Always draw name tag (even for self)
            name = player.get("name")
            if name:
                font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 14)
                name_surface = font.render(name, True, (0,0,0))
                name_rect = name_surface.get_rect(center=(x + image.get_width() // 2, y + image.get_height() + 15))
                self.config.screen.blit(name_surface, name_rect)

    def stop_wings(self) -> None:
        self.img_gen = cycle([self.img_idx])

    def resume_wings(self) -> None:
        self.img_gen = cycle([0, 1, 2, 1])
        self.frame = 0

    def flap(self) -> None:
        if self.y > self.min_y:
            self.vel_y = self.flap_acc
            self.flapped = True
            self.rot = 80
            self.config.sounds.wing.play()

    def crossed(self, pipe: Pipe) -> bool:
        return pipe.cx <= self.cx < pipe.cx - pipe.vel_x

    def collided(self, pipes: Pipes, floor: Floor) -> bool:
        """returns True if player collides with floor or pipes."""

        # if player crashes into ground
        if self.collide(floor):
            self.crashed = True
            self.crash_entity = "floor"
            return True

        for pipe in pipes.upper:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                return True
        for pipe in pipes.lower:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                return True

        return False
    
    def collided_push(self, pipes: Pipes) -> None:
        """Push player backwards if hit pipe (only in MULTI mode)"""
        if self.mode != PlayerMode.MULTI:
            return
            
        # Skip collision if in grace period
        if self.just_respawned:
            return
            
        for pipe in pipes.upper:
            if self.collide(pipe):
                self.x = pipe.x - self.w - 5
                return
            
        for pipe in pipes.lower:
            if self.collide(pipe):
                self.x = pipe.x - self.w - 5
                return
            
    def respawn(self, config: GameConfig) -> None:
        """Respawn player (only in MULTI mode)"""
        if self.mode != PlayerMode.MULTI:
            return
            
        # Check if player reached the left edge
        if self.x <= 0 and not self.waiting_to_respawn:
            self.waiting_to_respawn = True
            self.respawn_timer = 0
            
        # Handle respawn timer
        if self.waiting_to_respawn:
            self.respawn_timer += 1
            
            # Check if delay has passed
            if self.respawn_timer >= self.respawn_delay:
                # Actually respawn the player
                self.x = int(config.window.width * 0.2)
                self.y = int((config.window.height - self.h) / 2)
                self.vel_y = 0
                self.rot = 0
                
                # Reset respawn flags
                self.waiting_to_respawn = False
                self.respawn_timer = 0
                
                # Start post-respawn grace period
                self.just_respawned = True
                self.respawn_grace_timer = 0
        
        # Handle post-respawn grace period
        if self.just_respawned:
            self.respawn_grace_timer += 1
            if self.respawn_grace_timer >= self.respawn_grace_period:
                self.just_respawned = False
                self.respawn_grace_timer = 0