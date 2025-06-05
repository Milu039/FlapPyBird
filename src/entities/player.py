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
        x = 0  # Placeholder — will be set in reset or via multiplayer init
        y = 0
        super().__init__(config, image, x, y)

        self.img_idx = 0
        self.img_gen = cycle([0, 1, 2, 1])
        self.frame = 0
        self.id = 0
        self.skin_id = 0
        self.vel_x = 0

        self.respawn_timer = 0
        self.respawn_delay = 24
        self.waiting_to_respawn = False

        self.respawn_grace_period = 120
        self.respawn_grace_timer = 0
        self.just_respawned = False

        self.crashed = False
        self.crash_entity = None

        # Speed boost
        self.speed_boost_active = False
        self.speed_boost_timer = 0

        # Time freeze
        self.time_frozen = False
        self.freeze_timer = 0
        self.target_time_freeze = -1
        self.time_freeze_active = False

        # Penetration
        self.penetration_active = False
        self.penetration_timer = 0

        self.set_mode(PlayerMode.SHM)

    def set_mode(self, mode: PlayerMode) -> None:
        self.mode = mode
        if mode == PlayerMode.NORMAL:
            self.set_initial_position()
            self.reset_vals_normal()
            self.config.sounds.wing.play()
            self.resume_wings()
        elif mode == PlayerMode.SHM:
            self.set_initial_position()
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
            self.set_multiplayer_start_position()
            self.reset_vals_multi()
            self.resume_wings()

    def get_own_state(self):
        return self.x, self.y, self.rot, self.just_respawned, self.penetration_active, self.time_frozen
    
    def set_initial_position(self):
        self.x = int(self.config.window.width * 0.2)
        self.image = self.config.images.player[0]
        self.w = self.image.get_width()
        self.h = self.image.get_height()
        self.y = int((self.config.window.height - self.h) / 2)
        self.min_y = -2 * self.h
        self.max_y = self.config.window.viewport_height - self.h * 0.75

    def set_multiplayer_start_position(self):
        """Set position received from server in multiplayer mode"""
        if self.id == 0:
            self.x = 354
            self.y = 358
        elif self.id == 1:
            self.x = 304
            self.y = 358
        elif self.id == 2:
            self.x = 254
            self.y = 358
        elif self.id == 3:
            self.x = 204
            self.y = 358

    def reset(self) -> None:
        """Reset player to initial state before a new multiplayer game."""
        self.vel_y = 0
        self.rot = 0
        self.frame = 0
        self.img_idx = 0
        self.img_gen = cycle([0, 1, 2, 1])
        self.flapped = False
        self.vel_x = 0

        self.crashed = False
        self.crash_entity = None

        self.respawn_timer = 0
        self.respawn_delay = 24
        self.waiting_to_respawn = False
        self.respawn_grace_timer = 0
        self.just_respawned = False

        self.speed_boost_active = False
        self.speed_boost_timer = 0
        self.penetration_active = False
        self.penetration_timer = 0

        self.resume_wings()
        self.set_mode(PlayerMode.MULTI)

    def reset_vals_normal(self) -> None:
        self.vel_y = -9
        self.max_vel_y = 10
        self.min_vel_y = -8
        self.acc_y = 1

        self.rot = 80
        self.vel_rot = -3
        self.rot_min = -90
        self.rot_max = 20

        self.flap_acc = -9
        self.flapped = False

    def reset_vals_shm(self) -> None:
        self.vel_y = 1
        self.max_vel_y = 4
        self.min_vel_y = -4
        self.acc_y = 0.5

        self.rot = 0
        self.vel_rot = 0
        self.rot_min = 0
        self.rot_max = 0

        self.flap_acc = 0
        self.flapped = False

    def reset_vals_crash(self) -> None:
        self.acc_y = 2
        self.vel_y = 7
        self.max_vel_y = 15
        self.vel_rot = -8

    def reset_vals_multi(self) -> None:
        self.vel_y = -9
        self.max_vel_y = 10
        self.min_vel_y = -8
        self.vel_x = 0
        self.acc_y = 1

        self.rot = 80
        self.vel_rot = -3
        self.rot_min = -90
        self.rot_max = 20

        self.flap_acc = -9
        self.flapped = False

        self.waiting_to_respawn = False
        self.just_respawned = False
        self.respawn_timer = 0
        self.respawn_grace_timer = 0

    def update_image(self):
        self.frame += 1
        if self.frame % 5 == 0:
            self.img_idx = next(self.img_gen)
            if self.mode == PlayerMode.MULTI:
                self.image = self.config.images.skin[self.skin_id][self.img_idx]
            else:
                self.image = self.config.images.player[self.img_idx]
            self.w = self.image.get_width()
            self.h = self.image.get_height()

    def tick_shm(self):
        if self.vel_y >= self.max_vel_y or self.vel_y <= self.min_vel_y:
            self.acc_y *= -1
        self.vel_y += self.acc_y
        self.y += self.vel_y

    def tick_normal(self):
        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False
        self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
        self.rotate()

    def tick_crash(self):
        if self.min_y <= self.y <= self.max_y:
            self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
            if self.crash_entity != "floor":
                self.rotate()
        if self.vel_y < self.max_vel_y:
            self.vel_y += self.acc_y

    def tick_multi(self) -> None:
        """Update player position and state in MULTI mode"""
        # Time freeze logic
        if self.target_time_freeze == self.id:
            if self.time_frozen:
                self.freeze_timer -= 1
                if self.freeze_timer <= 0:
                    self.time_frozen = False
                return

        # Reduce speed boost timer if active
        if self.speed_boost_active:
            self.speed_boost_timer -= 1  # or subtract delta time
            if self.speed_boost_timer <= 0:
                self.speed_boost_active = False
                self.vel_x = 0  # Reset to normal speed

        # Apply horizontal velocity if in MULTI mode
        if self.mode == PlayerMode.MULTI:
            self.x += self.vel_x

        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False
        self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
        self.rotate()

        if self.penetration_active:
            self.penetration_timer -= 1 / self.config.fps
            if self.penetration_timer <= 0:
                self.penetration_active = False

    def rotate(self):
        self.rot = clamp(self.rot + self.vel_rot, self.rot_min, self.rot_max)

    def draw(self):
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

    def draw_player(self):
        if self.mode == PlayerMode.MULTI and self.waiting_to_respawn:
            return

        rotated_image = pygame.transform.rotate(self.image, self.rot)
        if self.mode == PlayerMode.MULTI:
            if self.just_respawned:
                if (self.respawn_grace_timer // 10) % 2 == 0:
                    return
                else:
                    rotated_image.set_alpha(255)
            elif self.penetration_active:
                rotated_image.set_alpha(128)

            elif self.target_time_freeze == self.id and self.time_freeze_active:
                

        rect = rotated_image.get_rect(center=self.rect.center)
        self.config.screen.blit(rotated_image, rect)

    def draw_other(self, players):
        for player in players:
            if player is None:
                continue
            first_player = max(players, key=lambda p: p["x"])
            player_id = player.get("player_id")
            skin_id = player.get("skin_id")
            x = player.get("x")
            y = player.get("y")
            rot = player.get("rot", 0)

            frame_idx = self.img_idx
            image = self.config.images.skin[skin_id][frame_idx]

            if player_id != self.id:
                rotated_image = pygame.transform.rotate(image, rot)
                if player.get("respawn"):
                    if (self.respawn_grace_timer // 10) % 2 == 0:
                        return
                    else:
                        rotated_image.set_alpha(255)
                elif player.get("penetration"):  # only if you're syncing skill states from server
                    rotated_image.set_alpha(128)
                elif player.get("time_freeze"):
                    

                rect = rotated_image.get_rect(center=(x + image.get_width() // 2, y + image.get_height() // 2))
                self.config.screen.blit(rotated_image, rect)

            name = player.get("name")
            if name:
                font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 14)
                name_surface = font.render(name, True, (0, 0, 0))
                name_rect = name_surface.get_rect(center=(x + image.get_width() // 2, y + image.get_height() + 15))
                self.config.screen.blit(name_surface, name_rect)

    def stop_wings(self):
        self.img_gen = cycle([self.img_idx])

    def resume_wings(self):
        self.img_gen = cycle([0, 1, 2, 1])
        self.frame = 0

    def flap(self):
        if self.y > self.min_y:
            self.vel_y = self.flap_acc
            self.flapped = True
            self.rot = 80
            self.config.sounds.wing.play()

    def crossed(self, pipe: Pipe) -> bool:
        return pipe.cx <= self.cx < pipe.cx - pipe.vel_x

    def collided(self, pipes: Pipes, floor: Floor) -> bool:
        if self.collide(floor):
            self.crashed = True
            self.crash_entity = "floor"
            return True

        for pipe in pipes.upper + pipes.lower:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                return True
        return False

    def collided_push(self, pipes: Pipes):
        if self.mode != PlayerMode.MULTI or self.just_respawned or self.penetration_active:
            return
        for pipe in pipes.upper + pipes.lower:
            if self.collide(pipe):
                self.x = pipe.x - self.w - 5
                return


    def respawn(self, config: GameConfig):
        if self.mode != PlayerMode.MULTI:
            return
        if self.x <= 0 and not self.waiting_to_respawn:
            self.waiting_to_respawn = True
            self.respawn_timer = 0
        if self.waiting_to_respawn:
            self.respawn_timer += 1
            if self.respawn_timer >= self.respawn_delay:
                self.set_initial_position()
                self.vel_y = 0
                self.rot = 0
                self.waiting_to_respawn = False
                self.just_respawned = True
                self.respawn_grace_timer = 0
        if self.just_respawned:
            self.respawn_grace_timer += 1
            if self.respawn_grace_timer >= self.respawn_grace_period:
                self.just_respawned = False
                self.respawn_grace_timer = 0
